"""Integration tests for auth endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.auth.models.email_verification_code import EmailVerificationCode

API = "/api/v1/auth"


class TestRegisterStart:
    """POST /auth/register/start"""

    async def test_new_email(self, client: AsyncClient):
        resp = await client.post(f"{API}/register/start", json={"email": "new@dezztech.com"})
        assert resp.status_code == 200
        assert resp.json()["ok"] is True
        assert resp.json()["already_registered"] is False

    async def test_personal_email_rejected(self, client: AsyncClient):
        resp = await client.post(f"{API}/register/start", json={"email": "user@gmail.com"})
        assert resp.status_code == 422

    async def test_invalid_email_format(self, client: AsyncClient):
        resp = await client.post(f"{API}/register/start", json={"email": "not-an-email"})
        assert resp.status_code == 422


class TestRegister:
    """POST /auth/register"""

    async def test_success(self, client: AsyncClient):
        resp = await client.post(
            f"{API}/register",
            json={
                "email": "register@dezztech.com",
                "password": "Test1234!",
                "first_name": "Test",
                "last_name": "User",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["otp_sent"] is True
        assert "user_id" in data

    async def test_personal_email_rejected(self, client: AsyncClient):
        resp = await client.post(
            f"{API}/register",
            json={
                "email": "user@gmail.com",
                "password": "Test1234!",
                "first_name": "Test",
                "last_name": "User",
            },
        )
        assert resp.status_code == 422

    async def test_weak_password_rejected(self, client: AsyncClient):
        resp = await client.post(
            f"{API}/register",
            json={
                "email": "weakpw@dezztech.com",
                "password": "12345678",
                "first_name": "Test",
                "last_name": "User",
            },
        )
        assert resp.status_code == 422


class TestVerifyEmail:
    """POST /auth/register/verify-email"""

    async def test_success(self, client: AsyncClient, db: AsyncSession):
        # Register
        await client.post(
            f"{API}/register",
            json={
                "email": "verify@dezztech.com",
                "password": "Test1234!",
                "first_name": "V",
                "last_name": "U",
            },
        )

        # Get OTP from DB
        result = await db.execute(
            select(EmailVerificationCode)
            .where(EmailVerificationCode.is_used.is_(False))
            .order_by(desc(EmailVerificationCode.created_at))
            .limit(1)
        )
        otp = result.scalar_one()

        resp = await client.post(
            f"{API}/register/verify-email",
            json={"email": "verify@dezztech.com", "code": otp.code},
        )
        assert resp.status_code == 200
        assert resp.json()["email_verified"] is True

    async def test_wrong_code(self, client: AsyncClient):
        await client.post(
            f"{API}/register",
            json={
                "email": "wrongotp@dezztech.com",
                "password": "Test1234!",
                "first_name": "W",
                "last_name": "O",
            },
        )

        resp = await client.post(
            f"{API}/register/verify-email",
            json={"email": "wrongotp@dezztech.com", "code": "0000"},
        )
        assert resp.status_code == 400
        assert resp.json()["error_code"] == "OTP_INVALID"


class TestLogin:
    """POST /auth/login"""

    async def test_success(self, client: AsyncClient, registered_user: dict):
        resp = await client.post(
            f"{API}/login",
            json={
                "email": registered_user["email"],
                "password": registered_user["password"],
            },
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    async def test_wrong_password(self, client: AsyncClient, registered_user: dict):
        resp = await client.post(
            f"{API}/login",
            json={"email": registered_user["email"], "password": "WrongPass1!"},
        )
        assert resp.status_code == 401
        assert resp.json()["error_code"] == "INVALID_CREDENTIALS"

    async def test_nonexistent_user(self, client: AsyncClient):
        resp = await client.post(
            f"{API}/login",
            json={"email": "nobody@dezztech.com", "password": "Test1234!"},
        )
        assert resp.status_code == 401

    async def test_unverified_email(self, client: AsyncClient):
        await client.post(
            f"{API}/register",
            json={
                "email": "unverified@dezztech.com",
                "password": "Test1234!",
                "first_name": "U",
                "last_name": "V",
            },
        )
        resp = await client.post(
            f"{API}/login",
            json={"email": "unverified@dezztech.com", "password": "Test1234!"},
        )
        assert resp.status_code == 400
        assert resp.json()["error_code"] == "EMAIL_NOT_VERIFIED"


class TestGetMe:
    """GET /auth/me"""

    async def test_authenticated(self, client: AsyncClient, registered_user: dict, auth_headers):
        resp = await client.get(f"{API}/me", headers=auth_headers(registered_user["token"]))
        assert resp.status_code == 200
        assert resp.json()["email"] == registered_user["email"]

    async def test_no_token(self, client: AsyncClient):
        resp = await client.get(f"{API}/me")
        assert resp.status_code == 401


class TestForgotPassword:
    """POST /auth/forgot-password"""

    async def test_existing_user(self, client: AsyncClient, registered_user: dict):
        resp = await client.post(
            f"{API}/forgot-password",
            json={"email": registered_user["email"]},
        )
        assert resp.status_code == 200
        assert resp.json()["ok"] is True

    async def test_nonexistent_user_no_leak(self, client: AsyncClient):
        """Should return 200 even for unknown emails (no information leak)."""
        resp = await client.post(
            f"{API}/forgot-password",
            json={"email": "ghost@dezztech.com"},
        )
        assert resp.status_code == 200
        assert resp.json()["ok"] is True


class TestResetPassword:
    """POST /auth/reset-password"""

    async def test_invalid_token(self, client: AsyncClient, registered_user: dict):
        await client.post(f"{API}/forgot-password", json={"email": registered_user["email"]})

        resp = await client.post(
            f"{API}/reset-password",
            json={
                "token": "invalid-token-that-does-not-exist",
                "password": "NewPass1234!",
                "confirm_password": "NewPass1234!",
            },
        )
        assert resp.status_code == 400
        assert resp.json()["error_code"] == "OTP_INVALID"

    async def test_passwords_dont_match(self, client: AsyncClient):
        resp = await client.post(
            f"{API}/reset-password",
            json={
                "token": "some-token-value-here",
                "password": "NewPass1234!",
                "confirm_password": "DifferentPass1!",
            },
        )
        assert resp.status_code == 422


class TestResendOtp:
    """POST /auth/register/resend-otp"""

    async def test_nonexistent_user(self, client: AsyncClient):
        resp = await client.post(
            f"{API}/register/resend-otp",
            json={"email": "ghost@dezztech.com"},
        )
        assert resp.status_code == 404
