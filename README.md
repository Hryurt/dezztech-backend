# Dezztech Backend

Dezztech Backend is a production-ready FastAPI backend for digitizing government incentive, grant, and support consulting operations. It enables companies and consultants to manage applications in one platform with speed, consistency, and traceability.

## 🏗️ Architecture

This project follows a **DDD-like modular monolith** architecture where each feature is organized into independent, self-contained modules. This approach provides:

- Clear separation of concerns
- Easy to understand and maintain
- Scalable to microservices if needed
- Reusable components

### Module Structure

Each module follows a consistent structure:

```
src/
├── {module_name}/
│   ├── router.py          # API endpoints
│   ├── schemas.py         # Pydantic models (request/response)
│   ├── models.py          # SQLAlchemy database models
│   ├── service.py         # Business logic
│   ├── dependencies.py    # FastAPI dependencies
│   ├── config.py          # Module-specific configuration
│   ├── constants.py       # Module constants
│   ├── exceptions.py      # Module-specific exceptions
│   └── utils.py           # Helper functions
```

## 🚀 Tech Stack

### Core
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern, fast web framework for building APIs
- **[Python 3.13](https://www.python.org/)** - Latest Python with performance improvements
- **[PostgreSQL 17](https://www.postgresql.org/)** - Robust relational database
- **[SQLAlchemy 2.0](https://www.sqlalchemy.org/)** - Async ORM for database operations
- **[Pydantic](https://docs.pydantic.dev/)** - Data validation and settings management
- **[Alembic](https://alembic.sqlalchemy.org/)** - Database migration tool

### Authentication & Security
- **[PyJWT](https://pyjwt.readthedocs.io/)** - JSON Web Token implementation
- **[Passlib](https://passlib.readthedocs.io/)** - Password hashing with bcrypt
- **[Bcrypt](https://github.com/pyca/bcrypt/)** - Secure password hashing algorithm

### Utilities
- **[slowapi](https://github.com/laurentS/slowapi)** - Rate limiting for FastAPI
- **[asyncpg](https://magicstack.github.io/asyncpg/)** - Fast PostgreSQL async driver

### Development Tools
- **[uv](https://github.com/astral-sh/uv)** - Fast Python package manager
- **[Ruff](https://docs.astral.sh/ruff/)** - Extremely fast Python linter and formatter
- **[Docker](https://www.docker.com/)** & **[Docker Compose](https://docs.docker.com/compose/)** - Containerization

## 📁 Project Structure

```
dezztech-backend/
├── alembic/                    # Database migrations
│   ├── versions/               # Migration files
│   └── env.py                  # Alembic environment configuration
├── src/
│   ├── auth/                   # Authentication module
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── service.py
│   │   ├── dependencies.py
│   │   ├── utils.py
│   │   ├── config.py
│   │   ├── constants.py
│   │   └── exceptions.py
│   ├── users/                  # Users module
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── service.py
│   │   ├── constants.py
│   │   └── exceptions.py
│   ├── config.py               # Global configuration
│   ├── constants.py            # Global constants
│   ├── database.py             # Database connection & session
│   ├── exceptions.py           # Global exception handlers
│   ├── logger.py               # Logging configuration
│   ├── pagination.py           # Pagination utilities
│   ├── rate_limit.py           # Rate limiting utilities
│   ├── models.py               # Global database models (mixins)
│   └── main.py                 # FastAPI application entry point
├── logs/                       # Application logs (auto-created)
├── .env                        # Environment variables (not in git)
├── .env.example                # Example environment variables
├── .gitignore                  # Git ignore rules
├── pyproject.toml              # Python dependencies & project metadata
├── uv.lock                     # Locked dependencies
├── alembic.ini                 # Alembic configuration
├── Dockerfile.dev              # Docker image for development
├── docker-compose.dev.yaml     # Docker Compose for development
└── README.md                   # This file
```

## 🔧 Setup & Installation

### Prerequisites

- **Docker** & **Docker Compose** (recommended)
- **Python 3.13+** (if running locally)
- **PostgreSQL 17** (if running locally without Docker)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd dezztech-backend
```

### 2. Environment Configuration

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database (Docker)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/dezztech_backend

# Database for Alembic migrations (Host)
ALEMBIC_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/dezztech_backend

# Environment
ENVIRONMENT=development

# Security
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# API
API_V1_PREFIX=/api/v1
PROJECT_NAME=Dezztech Backend

# CORS (JSON array)
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

### 3. Run with Docker (Recommended)

```bash
# Start PostgreSQL and FastAPI
docker compose -f docker-compose.dev.yaml up -d

# View logs
docker compose -f docker-compose.dev.yaml logs -f app

# Stop services
docker compose -f docker-compose.dev.yaml down
```

The API will be available at `http://localhost:8000`

### 4. Run Locally (Alternative)

Install dependencies:

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync
```

Start PostgreSQL (make sure it's running on port 5432).

Run migrations:

```bash
uv run alembic upgrade head
```

Start the application:

```bash
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## 📊 Database Migrations

### Create a New Migration

```bash
uv run alembic revision --autogenerate -m "description of changes"
```

### Apply Migrations

```bash
uv run alembic upgrade head
```

### Rollback Migration

```bash
# Rollback one version
uv run alembic downgrade -1

# Rollback to specific version
uv run alembic downgrade <revision_id>

# Rollback all
uv run alembic downgrade base
```

### View Migration History

```bash
uv run alembic history
uv run alembic current
```

## 🔐 API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/register` | Register new user | ❌ |
| POST | `/api/v1/auth/login` | Login user | ❌ |
| GET | `/api/v1/auth/me` | Get current user | ✅ |

### Root

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | API information | ❌ |
| GET | `/health` | Health check | ❌ |
| GET | `/docs` | Swagger UI | ❌ |
| GET | `/redoc` | ReDoc UI | ❌ |

### Example Requests

**Register:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "full_name": "John Doe"
  }'
```

**Login:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

**Get Current User:**
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer <your-access-token>"
```

## 🛠️ Development

### Code Quality

This project uses **Ruff** for linting and formatting:

```bash
# Run linter
uv run ruff check .

# Run linter with auto-fix
uv run ruff check . --fix

# Run formatter
uv run ruff format .
```

VS Code settings are included in `.vscode/settings.json` for automatic formatting on save.

### Adding a New Module

1. Create module directory: `src/{module_name}/`
2. Create required files:
   - `router.py` - API endpoints
   - `schemas.py` - Pydantic models
   - `models.py` - Database models
   - `service.py` - Business logic
   - `dependencies.py` - FastAPI dependencies
   - `config.py` - Module configuration
   - `constants.py` - Module constants
   - `exceptions.py` - Module exceptions
   - `utils.py` - Helper functions

3. Import models in `alembic/env.py`:
   ```python
   from src.{module_name}.models import *
   ```

4. Register router in `src/main.py`:
   ```python
   from src.{module_name}.router import router as {module_name}_router
   
   app.include_router(
       {module_name}_router,
       prefix=f"{settings.API_V1_PREFIX}/{module_name}",
       tags=["{Module Name}"]
   )
   ```

5. Create and apply migration:
   ```bash
   uv run alembic revision --autogenerate -m "add {module_name} table"
   uv run alembic upgrade head
   ```

### Logger Usage

The project includes a centralized logging system:

```python
from src.logger import get_logger

logger = get_logger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

Logs are written to:
- Console (stdout)
- `logs/app.log` (all logs)
- `logs/error.log` (errors only)

### Pagination Usage

Use built-in pagination utilities:

```python
from src.pagination import get_pagination_params, paginate, create_page_response

@router.get("/items", response_model=PageResponse[ItemResponse])
async def list_items(
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(get_pagination_params)
):
    query = select(Item).order_by(Item.created_at.desc())
    items, total = await paginate(db, query, pagination)
    return create_page_response(items, total, pagination)
```

### Rate Limiting Usage

Apply rate limits to endpoints:

```python
from src.rate_limit import limiter

@router.post("/login")
@limiter.limit("5/minute")
async def login(...):
    pass
```

## 🔒 Security Features

- **JWT Authentication** - Secure token-based authentication
- **Password Hashing** - Bcrypt for secure password storage
- **UUID Primary Keys** - Prevents enumeration attacks
- **Rate Limiting** - Protects against brute force and DDoS
- **CORS Configuration** - Controlled cross-origin requests
- **Input Validation** - Pydantic for request validation
- **SQL Injection Protection** - SQLAlchemy ORM parameterization

## 📝 Exception Handling

Global exception handling with i18n support:

- Custom `AppException` base class with `error_code` for frontend localization
- Specific HTTP exceptions (BadRequest, Unauthorized, NotFound, etc.)
- Pydantic validation error formatting
- Unhandled exception catching

All errors return consistent JSON format:

```json
{
  "error_code": "USER_NOT_FOUND",
  "error": "User not found",
  "details": { "user_id": "..." },
  "path": "/api/v1/users/123"
}
```

## 🧪 Testing

Tests are located in the `tests/` directory but are not currently implemented.

## 📦 Package Management

This project uses **uv** for fast, reliable package management:

```bash
# Add a package
uv add package-name

# Add a dev dependency
uv add --dev package-name

# Update packages
uv sync

# Lock dependencies
uv lock
```

## 🚀 Deployment

### Production Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure production `DATABASE_URL`
- [ ] Set up proper CORS origins
- [ ] Use Redis for rate limiting storage
- [ ] Configure proper logging (e.g., centralized logging)
- [ ] Set up database backups
- [ ] Use HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Set up monitoring and alerting

### Docker Production Build

Create a production `Dockerfile` and `docker-compose.yaml` (separate from `.dev` versions) with:
- Multi-stage builds for smaller images
- Non-root user
- Health checks
- Resource limits
- Production-grade web server (e.g., Gunicorn with Uvicorn workers)

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Run linter: `uv run ruff check . --fix`
4. Run formatter: `uv run ruff format .`
5. Test your changes
6. Submit a pull request

## 📧 Support

For issues and questions, please open an issue on GitHub.

---

**Built with ❤️ using FastAPI and modern Python tools**
