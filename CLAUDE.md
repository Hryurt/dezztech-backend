# Dezztech Backend — Claude Code Rehberi

## Proje Hakkinda

Dezztech Backend: Tesvik, hibe ve kamu destegi basvuru sureclerini yoneten FastAPI backend uygulamasi.

- **Framework:** FastAPI + SQLAlchemy (async) + PostgreSQL
- **Python:** 3.13
- **Migration:** Alembic (async)
- **Auth:** JWT (HS256, PyJWT) + OTP email dogrulama
- **Sifre:** bcrypt (passlib)

## Calisma Akisi

Bu projede PRD-tabanli adim adim gelistirme yapilir:

1. **PRD'yi oku:** `docs/PRD.md` — urun gereksinimleri
2. **Yapilanlari oku:** `docs/PROGRESS.md` — tamamlanan isler
3. Kullanici yeni task assign eder (ornek: "PRD 3.2'yi implement et")
4. Sorulari sor → cevap al
5. Implement et → test et → review yap
6. `docs/PROGRESS.md`'yi guncelle

**Her session basinda PRD ve PROGRESS dosyalarini oku.**

## Proje Yapisi

```
src/
├── main.py                    # FastAPI app, middleware, exception handlers
├── core/                      # Altyapi katmani
│   ├── config.py              # Pydantic Settings (.env)
│   ├── constants.py           # Global sabitler
│   ├── database.py            # Engine, session, Base, get_db
│   ├── exceptions.py          # AppException + handler'lar
│   ├── logger.py              # Logger factory
│   ├── models.py              # TimestampMixin
│   ├── pagination.py          # PaginationParams, paginate
│   ├── rate_limit.py          # slowapi limiter
│   └── security/
│       └── password_policy.py # Sifre validasyon
└── domains/                   # Is domain katmani
    ├── auth/                  # Kimlik dogrulama
    ├── users/                 # Kullanici yonetimi
    └── companies/             # Sirket yonetimi
```

Her domain su dosyalari icerir:
- `models.py` — SQLAlchemy modelleri (sadece domain/instance method'lar, classmethod YOK)
- `repository.py` — Veritabani sorgulari (tum DB erisimi buradan)
- `service.py` — Is mantigi (repository kullanir)
- `router.py` — FastAPI endpoint'leri
- `schemas.py` — Pydantic request/response sema'lari
- `exceptions.py` — Domain-ozel exception'lar
- `dependencies.py` — FastAPI dependency injection
- Opsiyonel: `config.py`, `constants.py`, `utils.py`

## Mimari Kurallar

- **Model'lerde classmethod KULLANMA.** Tum DB sorgulari `repository.py` icerisinde olur.
- **Service'ler repository uzerinden DB'ye erisir,** model'leri dogrudan cagirmaz.
- **Import pattern'lari:**
  - Core: `from src.core.config import settings`
  - Domain: `from src.domains.auth.service import AuthService`
- **Turk dilinde iletisim:** Kullanici Turkce konusur, kod ve degisken isimleri Ingilizce.

## Commit Kurallari

Format: `<action>: <message>` (max 50 karakter)

Action tipleri: `feat`, `fix`, `refactor`, `chore`, `docs`, `test`

**Co-Authored-By ekleme. Commit mesajina kendini koyma.**

## Komutlar

```bash
# Paket yonetimi: uv kullan (pip degil)
uv sync                            # dependency'leri kur
uv add <paket>                     # yeni dependency ekle
uv sync --group test               # test dependency'lerini kur

# Uygulamayi calistir (Docker)
docker compose -f docker-compose.dev.yaml up

# Lint
ruff check src/

# Test
uv run pytest                      # tum testler
uv run pytest tests/test_auth.py   # tek dosya
uv run pytest -x                   # ilk hatada dur

# Migration
alembic revision --autogenerate -m "description"
alembic upgrade head

# Import zinciri testi
DATABASE_URL="postgresql+asyncpg://x:x@localhost/x" SECRET_KEY="test" python -c "from src.main import app"
```
