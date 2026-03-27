"""Integration tests for user endpoints."""

from httpx import AsyncClient

API = "/api/v1/users"


class TestGetMe:
    """GET /users/me"""

    async def test_success(self, client: AsyncClient, registered_user: dict, auth_headers):
        resp = await client.get(f"{API}/me", headers=auth_headers(registered_user["token"]))
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == registered_user["email"]
        assert data["first_name"] == "Test"
        assert data["last_name"] == "User"
        assert data["has_password"] is True
        assert data["is_active"] is True

    async def test_no_token(self, client: AsyncClient):
        resp = await client.get(f"{API}/me")
        assert resp.status_code == 401


class TestUpdateMe:
    """PATCH /users/me"""

    async def test_update_name(self, client: AsyncClient, registered_user: dict, auth_headers):
        headers = auth_headers(registered_user["token"])
        resp = await client.patch(
            f"{API}/me",
            headers=headers,
            json={"first_name": "Updated", "last_name": "Name"},
        )
        assert resp.status_code == 200
        assert resp.json()["first_name"] == "Updated"
        assert resp.json()["last_name"] == "Name"

    async def test_update_phone(self, client: AsyncClient, registered_user: dict, auth_headers):
        headers = auth_headers(registered_user["token"])
        resp = await client.patch(
            f"{API}/me",
            headers=headers,
            json={"phone_number": "+905551234567"},
        )
        assert resp.status_code == 200
        assert resp.json()["phone_number"] == "+905551234567"

    async def test_partial_update(self, client: AsyncClient, registered_user: dict, auth_headers):
        """Only provided fields should change."""
        headers = auth_headers(registered_user["token"])
        resp = await client.patch(
            f"{API}/me",
            headers=headers,
            json={"first_name": "OnlyFirst"},
        )
        assert resp.status_code == 200
        assert resp.json()["first_name"] == "OnlyFirst"


class TestChangePassword:
    """PATCH /users/me/password"""

    async def test_success(self, client: AsyncClient, registered_user: dict, auth_headers):
        headers = auth_headers(registered_user["token"])
        resp = await client.patch(
            f"{API}/me/password",
            headers=headers,
            json={
                "current_password": registered_user["password"],
                "new_password": "NewPass1234!",
                "confirm_password": "NewPass1234!",
            },
        )
        assert resp.status_code == 204

    async def test_wrong_current_password(
        self, client: AsyncClient, registered_user: dict, auth_headers
    ):
        headers = auth_headers(registered_user["token"])
        resp = await client.patch(
            f"{API}/me/password",
            headers=headers,
            json={
                "current_password": "WrongCurrent1!",
                "new_password": "NewPass1234!",
                "confirm_password": "NewPass1234!",
            },
        )
        assert resp.status_code == 401
        assert resp.json()["error_code"] == "INVALID_CREDENTIALS"

    async def test_same_password(self, client: AsyncClient, registered_user: dict, auth_headers):
        headers = auth_headers(registered_user["token"])
        resp = await client.patch(
            f"{API}/me/password",
            headers=headers,
            json={
                "current_password": registered_user["password"],
                "new_password": registered_user["password"],
                "confirm_password": registered_user["password"],
            },
        )
        assert resp.status_code == 400
        assert resp.json()["error_code"] == "PASSWORD_REUSE_NOT_ALLOWED"

    async def test_passwords_dont_match(
        self, client: AsyncClient, registered_user: dict, auth_headers
    ):
        headers = auth_headers(registered_user["token"])
        resp = await client.patch(
            f"{API}/me/password",
            headers=headers,
            json={
                "current_password": registered_user["password"],
                "new_password": "NewPass1234!",
                "confirm_password": "DifferentPass1!",
            },
        )
        assert resp.status_code == 422


class TestDeactivateAccount:
    """DELETE /users/me"""

    async def test_success(self, client: AsyncClient, registered_user: dict, auth_headers):
        headers = auth_headers(registered_user["token"])
        resp = await client.request(
            "DELETE",
            f"{API}/me",
            headers=headers,
            json={"current_password": registered_user["password"]},
        )
        assert resp.status_code == 204

    async def test_wrong_password(self, client: AsyncClient, registered_user: dict, auth_headers):
        headers = auth_headers(registered_user["token"])
        resp = await client.request(
            "DELETE",
            f"{API}/me",
            headers=headers,
            json={"current_password": "WrongPass1!"},
        )
        assert resp.status_code == 401


class TestSetPassword:
    """POST /users/me/set-password (for OAuth users)"""

    async def test_already_has_password(
        self, client: AsyncClient, registered_user: dict, auth_headers
    ):
        """User registered with password should get error."""
        headers = auth_headers(registered_user["token"])
        resp = await client.post(
            f"{API}/me/set-password",
            headers=headers,
            json={
                "new_password": "SetPass1234!",
                "confirm_password": "SetPass1234!",
            },
        )
        assert resp.status_code == 400
        assert resp.json()["error_code"] == "PASSWORD_ALREADY_SET"
