# AGENTS.md

Bu dosya, `/Users/hry/Documents/Dezztech/dezztech-backend` dizini ve altındaki tüm dosyalar için çalışma kurallarını tanımlar.

## Proje Özeti

- Proje adı: `Dezztech Backend`
- Amaç: Devlet teşvik, hibe ve destek başvuru süreçlerini şirketler ve danışmanlar için dijital ortamda yönetmek.
- Mimari: DDD benzeri, modüler monolith.

## Tech Stack

- FastAPI
- PostgreSQL
- SQLAlchemy ORM 2.0 (async)
- Pydantic / pydantic-settings
- Alembic
- uv (paket yönetimi)
- Ruff (lint/format)

## Klasör Yapısı

Temel yapı aşağıdaki gibidir:

```text
dezztech-backend
├── alembic/
├── src/
│   ├── auth/
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── models.py
│   │   ├── dependencies.py
│   │   ├── config.py
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   ├── service.py
│   │   └── utils.py
│   ├── users/
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── models.py
│   │   ├── dependencies.py
│   │   ├── config.py
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   ├── service.py
│   │   └── utils.py
│   ├── config.py
│   ├── models.py
│   ├── exceptions.py
│   ├── pagination.py
│   ├── rate_limit.py
│   ├── logger.py
│   ├── database.py
│   └── main.py
├── tests/  # Şu an test yok; test yazımı bu aşamada zorunlu değil.
├── .env
├── .env.example
├── pyproject.toml
├── docker-compose.dev.yaml
└── README.md
```

## Yeni Modül Açma Standardı

Yeni bir modül eklenecekse aşağıdaki dosyalar eksiksiz oluşturulmalıdır:

- `router.py`
- `schemas.py`
- `models.py`
- `dependencies.py`
- `config.py`
- `constants.py`
- `exceptions.py`
- `service.py`
- `utils.py`

## DDD Katman Prensipleri

### `models.py`

- SQLAlchemy modelleri + entity seviyesinde domain davranışı içerir.
- Instance method'lar entity durumunu değiştirir, doğrudan commit etmez.
- Query amaçlı classmethod'lar async çalışır ve `AsyncSession` alır.

### `service.py`

- İş akışlarının orkestrasyon katmanıdır.
- Class-based service kullanılmalı (`__init__(self, db: AsyncSession)`).
- Transaction, hata yönetimi ve loglama burada yapılmalı.

### `dependencies.py`

- FastAPI dependency factory fonksiyonları içerir.
- Service instance üretimi bu katmandan yapılır.

### `router.py`

- HTTP katmanı ince tutulmalı.
- Business logic doğrudan router'da yazılmamalı, service'e delege edilmeli.

### `schemas.py`

- Pydantic request/response modelleri.
- İş kuralı değil, doğrulama ve serileştirme odaklı olmalı.

## Kodlama Kuralları

- Python 3.13 ile uyumlu yaz.
- Tüm endpoint'ler async olmalı.
- Public API response'larında tutarlı şema kullan.
- Hata yönetiminde proje exception yapısını kullan.
- Konfigürasyon için `src/config.py` ve `.env` kaynak alınmalı.

## Çalıştırma ve Kontrol

Değişikliklerden sonra mümkünse aşağıdaki kontroller çalıştırılmalı:

```bash
uv run ruff check .
uv run ruff format .
uv run python -m compileall src
```

## Operasyonel Notlar

- Mevcut dosya yapısını koru, keyfi yeniden adlandırma yapma.
- Docker servis isimleri ve `.env` örnekleri Dezztech adlandırmasıyla uyumlu olmalı.
- Güvenlik ayarlarında token süreleri `.env` ve `src/config.py` üzerinden yönetilmeli.
