"""Shared test fixtures.

Uses a separate test database (dezztech_backend_test) with real PostgreSQL.
Each test gets its own engine/session factory to avoid asyncpg connection conflicts.
"""

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import settings
from src.core.database import Base, get_db

# Import all models so Base.metadata knows about them
import src.domains.auth.models  # noqa: F401
import src.domains.companies.models  # noqa: F401
import src.domains.users.models  # noqa: F401

# ── Test database URL ──
_base_url = str(settings.ALEMBIC_DATABASE_URL or settings.DATABASE_URL)
parts = _base_url.rsplit("/", 1)
TEST_DATABASE_URL = parts[0] + "/dezztech_backend_test"


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Create all tables once before tests, seed required data, drop after."""
    from src.domains.companies.models import CompanyRole

    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    # Seed company roles
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        for role_name in ("owner", "admin", "accountant", "viewer"):
            session.add(CompanyRole(name=role_name, permissions=[], is_active=True))
        await session.commit()
    await engine.dispose()
    yield
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient]:
    """Provide an HTTP test client with its own isolated engine.

    After the test, disposes the engine and truncates all tables.
    """
    from src.main import app

    # Each test gets a fresh engine
    test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    test_session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async def _override_get_db():
        async with test_session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = _override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()

    # Dispose all connections from this engine first
    await test_engine.dispose()

    # Truncate with a fresh short-lived engine
    cleanup_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with cleanup_engine.begin() as conn:
        # Don't truncate company_roles — seeded once per session
        tables_to_clean = [
            t.name for t in Base.metadata.sorted_tables if t.name != "company_roles"
        ]
        table_names = ", ".join(tables_to_clean)
        await conn.exec_driver_sql(f"TRUNCATE {table_names} CASCADE")
    await cleanup_engine.dispose()


@pytest.fixture
async def db() -> AsyncGenerator[AsyncSession]:
    """Provide a standalone DB session for direct queries in tests."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


# ── Helper fixtures ──


@pytest.fixture
def auth_headers():
    """Factory fixture to create auth headers from a token."""

    def _make(token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    return _make


async def _create_verified_user(
    client: AsyncClient,
    email: str = "testuser@dezztech.com",
    password: str = "Test1234!",
    first_name: str = "Test",
    last_name: str = "User",
) -> dict:
    """Helper: register, verify email, login. Returns user info dict."""
    from sqlalchemy import desc, select

    from src.domains.auth.models.email_verification_code import EmailVerificationCode

    # Register
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
        },
    )
    assert resp.status_code == 201
    user_id = resp.json()["user_id"]

    # Get OTP from DB via a short-lived session
    otp_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    otp_factory = async_sessionmaker(otp_engine, class_=AsyncSession, expire_on_commit=False)
    async with otp_factory() as session:
        result = await session.execute(
            select(EmailVerificationCode)
            .where(EmailVerificationCode.is_used.is_(False))
            .order_by(desc(EmailVerificationCode.created_at))
            .limit(1)
        )
        otp = result.scalar_one()
        code = otp.code
    await otp_engine.dispose()

    # Verify email
    verify_resp = await client.post(
        "/api/v1/auth/register/verify-email",
        json={"email": email, "code": code},
    )
    assert verify_resp.status_code == 200

    # Login
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    return {
        "email": email,
        "password": password,
        "user_id": user_id,
        "token": token,
    }


@pytest.fixture
async def registered_user(client: AsyncClient) -> dict:
    """Create and verify a registered user, return user info with token."""
    return await _create_verified_user(client)
