# Dezztech Backend — Yapilan Isler

> Bu dosya her sprint/task sonunda guncellenir. Claude Code tarafindan otomatik doldurulur.
> PRD referansi: `docs/PRD.md`

---

## PRD Kapsam Eslestirmesi

| PRD Bolum | Konu | Durum |
|-----------|------|-------|
| 5.1.1 | Kayit (email + OTP + Google + Microsoft) | Tamamlandi |
| 5.1.2 | Giris (email + sifre + Google + Microsoft) | Tamamlandi |
| 5.1.3 | Parola yonetimi | Tamamlandi |
| 5.1.4 | Profil yonetimi | Tamamlandi |
| 5.2 | Firma yonetimi | Tamamlandi |
| 5.3 | Urun yonetimi | Yapilmadi |
| 5.4 | Tesvik ve destek yonetimi | Yapilmadi |
| 5.5 | Basvuru yonetimi | Yapilmadi |
| 5.6 | Yapay zeka modulleri | Yapilmadi |
| 5.7 | Admin senaryolari | Yapilmadi |
| 5.8 | Super Admin senaryolari | Yapilmadi |
| 4 | Abonelik modeli | Kismen — model + limitler tamam, odeme entegrasyonu yok |
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
- [x] Is emaili kisitlamasi (blocklist: gmail, hotmail, yahoo, yandex, icloud vb.)
- [x] Email + sifre ile giris → JWT access token (HS256)
- [x] Google OAuth giris/kayit (POST /auth/google — id_token dogrulama, otomatik kayit)
- [x] Microsoft OAuth giris/kayit (POST /auth/microsoft — JWKS dogrulama, otomatik kayit)
- [x] OAuth kullanicilar icin sifreli/sifresiz hesap destegi (password_hash nullable)
- [x] Sifre olusturma (POST /users/me/set-password — OAuth hesaplar icin)
- [x] Sifre degistirme (mevcut sifre dogrulama + yeni sifre validasyon)
- [x] Sifresiz kullanici sifre ile giris yapamaz (PASSWORD_NOT_SET hatasi)
- [x] Sifre sifirlama (forgot-password → token → reset-password)
- [x] Profil goruntuleme ve guncelleme (first_name, last_name, phone_number)
- [x] Email degistirme (OTP ile dogrulama)
- [x] Hesap deaktivasyonu (soft delete)
- [x] Rol tabanli erisim kontrolu (require_role, require_superuser)
- [x] has_password alani UserMeResponse'a eklendi

### Yapilmadi (PRD gereksinimleri)
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
| POST | /api/v1/auth/google | Tamamlandi |
| POST | /api/v1/auth/microsoft | Tamamlandi |
| GET | /api/v1/users/me | Tamamlandi |
| PATCH | /api/v1/users/me | Tamamlandi |
| PATCH | /api/v1/users/me/password | Tamamlandi |
| POST | /api/v1/users/me/email-change-request | Tamamlandi |
| POST | /api/v1/users/me/email-change-verify | Tamamlandi |
| POST | /api/v1/users/me/set-password | Tamamlandi |
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
- [x] PRD 8.2 ortak firma alanlari tamamlandi (sgk_debt, tax_debt, financials, contact_email, activity_sectors JSON, exporter_unions JSON)
- [x] CompanyBrand modeli (PRD 8.2 — tekrarlanabilir marka, yurt ici/disi tescil)
- [x] CompanySectorProfile modeli (PRD 8.3 — sektore ozel alanlar, EAV pattern, form builder uyumlu field_key ile)

### Yapilmadi (PRD gereksinimleri)
- [x] Kullanici davet etme (PRD 5.2.5 — invite + accept, email ile, 7 gun token suresi)
- [x] Kayitli olmayan kullanici davet kabul ederek kayit olabilir
- [x] Consultant rolu sadece Admin sistem rolune sahip kullanicilara atanabilir
- [x] Email servisi (SendGrid, development'ta loglama)
- [x] CompanyInvitation modeli
- [x] Firma silme (hard delete — PRD 5.2.4, sadece Owner)
- [x] Abonelik bazli firma olusturma limiti (PRD 5.2.7)
- [x] Abonelik bazli uyelik limiti (PRD 5.2.7 — uyeler + bekleyen davetler sayilir)
- [ ] CompanyBrand CRUD endpoint'leri
- [ ] CompanySectorProfile CRUD endpoint'leri

### Modeller
- Company — PRD 8.2 tam: kimlik, finans (sgk/vergi borcu, ihracat gelirleri), aktivite (activity_sectors JSON, exporter_unions JSON), iletisim (contact_email eklendi)
- CompanyRole — name, permissions (JSON), is_active (owner/admin/accountant/viewer)
- UserCompany — user_id, company_id, role_id, is_active (many-to-many with role)
- CompanySector — company_id, nace_code, nace_name, brand_name
- CompanyBrand — company_id, brand_name, brand_url
- CompanySectorProfile — company_id (unique, one-to-one), sector_type, data (JSON)
- CompanyInvitation — **YENI** company_id, email, role_id, invited_by, token, expires_at, is_accepted

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
| POST | /api/v1/companies/{id}/invite-user | Tamamlandi |
| DELETE | /api/v1/companies/{id} | Tamamlandi |
| POST | /api/v1/companies/invitations/accept | Tamamlandi |

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

### Yapilan
- [x] UserSubscription modeli (plan tier, billing cycle, extra quotas)
- [x] 4 plan tieri: freemium, basic, pro, premium (PRD 4.1 limitleri)
- [x] Kayit sirasinda otomatik Freemium atama (register, OAuth, invite accept)
- [x] A la carte ek haklar (extra_company_quota, extra_product/member_quota_per_company)
- [x] Firma olusturma limiti enforcement (freemium engeli + plan limiti)
- [x] Uye davet limiti enforcement (uyeler + bekleyen davetler sayilir)
- [x] GET /subscriptions/me — kullanicinin abonelik bilgisi
- [x] PUT /subscriptions/change-plan — Super Admin plan degistirme
- [x] PUT /subscriptions/extra-quotas — Super Admin ek hak guncelleme
- [x] GET /subscriptions/{user_id} — Super Admin kullanici abonelik goruntuleme

### Yapilmadi
- [ ] iyzico odeme entegrasyonu
- [ ] Abonelik fiyatlandirmasi
- [ ] Otomatik yenileme / iptal akisi

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
- [ ] password_hash nullable migration olusturulmali (OAuth desteği icin)
- [ ] Email gonderimi entegrasyonu yok (OTP ve bildirimler sadece loglaniyor)
- [ ] Test altyapisi yok
- [ ] CI/CD pipeline yok
