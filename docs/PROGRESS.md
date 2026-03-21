# Dezztech Backend — Yapilan Isler

> Bu dosya her sprint/task sonunda guncellenir. Claude Code tarafindan otomatik doldurulur.
> PRD referansi: `docs/PRD.md`

---

## PRD Kapsam Eslestirmesi

| PRD Bolum | Konu | Durum |
|-----------|------|-------|
| 5.1.1 | Kayit (email + OTP) | Kismen — is emaili kisitlamasi ve OAuth yok |
| 5.1.2 | Giris (email + sifre) | Tamamlandi — OAuth yok |
| 5.1.3 | Parola yonetimi | Tamamlandi |
| 5.1.4 | Profil yonetimi | Tamamlandi |
| 5.2 | Firma yonetimi | Kismen — davet placeholder, silme yok, abonelik limiti yok |
| 5.3 | Urun yonetimi | Yapilmadi |
| 5.4 | Tesvik ve destek yonetimi | Yapilmadi |
| 5.5 | Basvuru yonetimi | Yapilmadi |
| 5.6 | Yapay zeka modulleri | Yapilmadi |
| 5.7 | Admin senaryolari | Yapilmadi |
| 5.8 | Super Admin senaryolari | Yapilmadi |
| 4 | Abonelik modeli | Yapilmadi |
| 10 | Dezzcovery soru seti | Yapilmadi |
| 11 | Bildirim sistemi | Yapilmadi |
| 12 | Dashboard | Yapilmadi |

---

## Proje Altyapisi

- [x] FastAPI proje iskeleti (main.py, lifespan, CORS, middleware)
- [x] PostgreSQL + SQLAlchemy async engine & session yonetimi
- [x] Alembic migration altyapisi (async)
- [x] Pydantic Settings (.env tabanli konfigurasyon)
- [x] Loglama altyapisi (console + file + error file)
- [x] Global exception handler (AppException, HTTP, Validation, Unhandled)
- [x] Global pagination (PaginationParams, PageResponse, paginate helper)
- [x] Rate limiter (slowapi — public, authenticated, strict profilleri)
- [x] TimestampMixin (created_at, updated_at)
- [x] Password policy (regex tabanli, merkezi — core/security/password_policy.py)
- [x] Health check & root endpoint

## Mimari (Son Durum)

```
src/
├── main.py
├── core/           # Altyapi katmani
│   ├── config, constants, database, exceptions
│   ├── logger, models, pagination, rate_limit
│   └── security/password_policy.py
└── domains/        # Is domain katmani
    ├── auth/       # Kimlik dogrulama
    ├── users/      # Kullanici yonetimi
    └── companies/  # Sirket yonetimi
```

Her domain: `models.py`, `repository.py`, `service.py`, `router.py`, `schemas.py`, `exceptions.py`, `dependencies.py` + opsiyonel `config.py`, `constants.py`, `utils.py`

---

## PRD 5.1 — Kimlik Dogrulama ve Hesap Yonetimi

### Yapilan
- [x] Email + sifre ile kayit (register/start → register → verify-email)
- [x] OTP ile email dogrulama (4 haneli, 10dk gecerlilik, max 5 deneme, 60sn cooldown)
- [x] Email + sifre ile giris → JWT access token (HS256)
- [x] Sifre sifirlama (forgot-password → token → reset-password)
- [x] Sifre degistirme (mevcut sifre dogrulama + yeni sifre validasyon)
- [x] Profil goruntuleme ve guncelleme (first_name, last_name, phone_number)
- [x] Email degistirme (OTP ile dogrulama)
- [x] Hesap deaktivasyonu (soft delete)
- [x] Rol tabanli erisim kontrolu (require_role, require_superuser)

### Yapilmadi (PRD gereksinimleri)
- [ ] Is emaili kisitlamasi (genel email saglayicilari engellenmeli — PRD 5.1.1.1)
- [ ] Google OAuth giris (PRD 5.1.1.3, 5.1.2.2)
- [ ] Microsoft Outlook OAuth giris (PRD 5.1.1.3, 5.1.2.2)
- [ ] Refresh token mekanizmasi

### Modeller
- User — email, password_hash, first_name, last_name, role (user/admin/super_admin), email_verified_at, phone_number, how_did_you_hear, pending_email, is_active
- EmailVerificationCode — OTP kodu, max 5 deneme, 60sn cooldown, 10dk gecerlilik
- PasswordResetToken — SHA256 hash token, 15dk gecerlilik, tek kullanimlik

### Endpoint'ler
| Method | Endpoint | Durum |
|--------|----------|-------|
| POST | /api/v1/auth/register/start | Tamamlandi |
| POST | /api/v1/auth/register | Tamamlandi |
| POST | /api/v1/auth/register/verify-email | Tamamlandi |
| POST | /api/v1/auth/register/resend-otp | Tamamlandi |
| POST | /api/v1/auth/login | Tamamlandi |
| GET | /api/v1/auth/me | Tamamlandi |
| POST | /api/v1/auth/forgot-password | Tamamlandi |
| POST | /api/v1/auth/reset-password | Tamamlandi |
| GET | /api/v1/users/me | Tamamlandi |
| PATCH | /api/v1/users/me | Tamamlandi |
| PATCH | /api/v1/users/me/password | Tamamlandi |
| POST | /api/v1/users/me/email-change-request | Tamamlandi |
| POST | /api/v1/users/me/email-change-verify | Tamamlandi |
| DELETE | /api/v1/users/me | Tamamlandi |

---

## PRD 5.2 — Firma Yonetimi

### Yapilan
- [x] Firma olusturma (temel + profil/finans/iletisim alanlari)
- [x] Olusturan kullanici otomatik owner olur
- [x] MERSIS numarasi benzersizlik kontrolu
- [x] Firma listeleme (sayfalama + arama)
- [x] Firma detay goruntuleme
- [x] Firma guncelleme (partial update)
- [x] Firma aktivasyon/deaktivasyonu
- [x] Uyelik tabanli erisim kontrolu (member / admin+owner)
- [x] SUPER_ADMIN tum sirketlere sentetik owner erisimi
- [x] Sektor CRUD (NACE kodu company bazinda unique)
- [x] IBAN normalizasyonu

### Yapilmadi (PRD gereksinimleri)
- [ ] Kullanici davet etme is mantigi (endpoint placeholder var — PRD 5.2.5)
- [ ] Firma silme (hard delete — PRD 5.2.4, sadece Owner)
- [ ] Abonelik bazli firma olusturma limiti (PRD 5.2.7)
- [ ] Abonelik bazli uyelik limiti (PRD 5.2.7)
- [ ] PRD 8.2-8.4'teki ek firma alanlari (SGK/vergi borcu, sektore ozel alanlar, markalaşma alanlari)

### Modeller
- Company — name, mersis_number, tax_number, tax_office, employee_count, is_active + profil/finans/iletisim alanlari
- CompanyRole — name, permissions (JSON), is_active (owner/admin/accountant/viewer)
- UserCompany — user_id, company_id, role_id, is_active (many-to-many with role)
- CompanySector — company_id, nace_code, nace_name, brand_name

### Endpoint'ler
| Method | Endpoint | Durum |
|--------|----------|-------|
| POST | /api/v1/companies | Tamamlandi |
| GET | /api/v1/companies/my | Tamamlandi |
| GET | /api/v1/companies/{id} | Tamamlandi |
| PATCH | /api/v1/companies/{id} | Tamamlandi |
| PATCH | /api/v1/companies/{id}/deactivate | Tamamlandi |
| PATCH | /api/v1/companies/{id}/activate | Tamamlandi |
| GET | /api/v1/companies/{id}/members | Tamamlandi |
| GET | /api/v1/companies/{id}/sectors | Tamamlandi |
| POST | /api/v1/companies/{id}/sectors | Tamamlandi |
| PATCH | /api/v1/companies/{id}/sectors/{sid} | Tamamlandi |
| DELETE | /api/v1/companies/{id}/sectors/{sid} | Tamamlandi |
| POST | /api/v1/companies/{id}/invite-user | Placeholder |

---

## PRD 5.3 — Urun Yonetimi

Henuz baslanmadi.

---

## PRD 5.4 — Tesvik ve Destek Yonetimi

Henuz baslanmadi.

---

## PRD 5.5 — Basvuru Yonetimi

Henuz baslanmadi.

---

## PRD 5.6 — Yapay Zeka Modulleri

Henuz baslanmadi.

---

## PRD 4 — Abonelik Modeli

Henuz baslanmadi.

---

## Veritabani Migration'lari

| Tarih | Migration | Durum |
|-------|-----------|-------|
| 2026-01-12 | create_users_table_with_uuid | Tamamlandi |
| 2026-02-24 | update_users_table_to_new_structure | Tamamlandi |
| 2026-02-25 | add_email_verification_codes_table | Tamamlandi |
| 2026-02-25 | add_password_reset_token_table | Tamamlandi |
| 2026-02-25 | add_phone_number_and_how_did_you_hear_to_users | Tamamlandi |
| 2026-02-26 | add_pending_email_to_users | Tamamlandi |
| 2026-02-26 | add_profile_image_url_to_users | Tamamlandi |
| 2026-02-26 | remove_profile_image_url_from_users | Tamamlandi |

> Not: Companies domain migration dosyalari git'te silindi (branch-local calismada silinmis). Yeni migration olusturulmali.

---

## Repository Katmani

- [x] UserRepository (get_by_id, get_by_email, exists, email_or_pending_exists, get_active_users, create)
- [x] AuthRepository (create_verification_code, get_latest_active_verification_code, create_reset_token, get_active_reset_token, invalidate_active_tokens)
- [x] CompanyRepository (company CRUD, role lookup, membership CRUD, sector CRUD, paginated listing)

---

## Bilinen Eksikler / Teknik Borc

- [ ] Companies domain migration dosyalari eksik (silinmis, yeniden olusturulmali)
- [ ] Email gonderimi entegrasyonu yok (OTP ve bildirimler sadece loglaniyor)
- [ ] Test altyapisi yok
- [ ] CI/CD pipeline yok
