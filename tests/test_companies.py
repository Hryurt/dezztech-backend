"""Integration tests for company endpoints."""

import uuid

from httpx import AsyncClient

API = "/api/v1/companies"


def _company_payload(**overrides) -> dict:
    """Build a valid company creation payload."""
    base = {
        "name": "Test Sirket A.S.",
        "mersis_number": "1234567890123456",
        "tax_number": "1234567890",
        "tax_office": "Istanbul",
        "employee_count": 10,
    }
    base.update(overrides)
    return base


class TestCreateCompany:
    """POST /companies"""

    async def test_success(self, client: AsyncClient, basic_user: dict, auth_headers):
        headers = auth_headers(basic_user["token"])
        resp = await client.post(f"{API}", headers=headers, json=_company_payload())
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Test Sirket A.S."
        assert data["is_active"] is True

    async def test_duplicate_mersis(self, client: AsyncClient, auth_headers):
        """Needs Pro plan (2 company limit) to test MERSIS duplicate vs limit."""
        from tests.conftest import _create_verified_user, _upgrade_plan

        user = await _create_verified_user(client, email="dupmersis@dezztech.com")
        await _upgrade_plan(user["user_id"], "pro")
        headers = auth_headers(user["token"])

        await client.post(f"{API}", headers=headers, json=_company_payload(mersis_number="DUP12345"))
        resp = await client.post(
            f"{API}", headers=headers, json=_company_payload(mersis_number="DUP12345")
        )
        assert resp.status_code == 409
        assert resp.json()["error_code"] == "COMPANY_MERSIS_CONFLICT"

    async def test_unauthenticated(self, client: AsyncClient):
        resp = await client.post(f"{API}", json=_company_payload())
        assert resp.status_code == 401


class TestListMyCompanies:
    """GET /companies/my"""

    async def test_success(self, client: AsyncClient, basic_user: dict, auth_headers):
        headers = auth_headers(basic_user["token"])
        await client.post(f"{API}", headers=headers, json=_company_payload(mersis_number="LIST0001"))

        resp = await client.get(f"{API}/my", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        assert len(data["items"]) >= 1

    async def test_unauthenticated(self, client: AsyncClient):
        resp = await client.get(f"{API}/my")
        assert resp.status_code == 401


class TestGetCompany:
    """GET /companies/{id}"""

    async def test_success(self, client: AsyncClient, basic_user: dict, auth_headers):
        headers = auth_headers(basic_user["token"])
        create_resp = await client.post(
            f"{API}", headers=headers, json=_company_payload(mersis_number="GET00001")
        )
        company_id = create_resp.json()["id"]

        resp = await client.get(f"{API}/{company_id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == company_id

    async def test_not_member(self, client: AsyncClient, basic_user: dict, auth_headers):
        headers = auth_headers(basic_user["token"])
        fake_id = str(uuid.uuid4())
        resp = await client.get(f"{API}/{fake_id}", headers=headers)
        assert resp.status_code == 403


class TestUpdateCompany:
    """PATCH /companies/{id}"""

    async def test_success(self, client: AsyncClient, basic_user: dict, auth_headers):
        headers = auth_headers(basic_user["token"])
        create_resp = await client.post(
            f"{API}", headers=headers, json=_company_payload(mersis_number="UPD00001")
        )
        company_id = create_resp.json()["id"]

        resp = await client.patch(
            f"{API}/{company_id}",
            headers=headers,
            json={"name": "Updated Sirket", "employee_count": 50},
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated Sirket"
        assert resp.json()["employee_count"] == 50


class TestDeleteCompany:
    """DELETE /companies/{id}"""

    async def test_owner_can_delete(
        self, client: AsyncClient, basic_user: dict, auth_headers
    ):
        headers = auth_headers(basic_user["token"])
        create_resp = await client.post(
            f"{API}", headers=headers, json=_company_payload(mersis_number="DEL00001")
        )
        company_id = create_resp.json()["id"]

        resp = await client.delete(f"{API}/{company_id}", headers=headers)
        assert resp.status_code == 204

        # Verify it's gone
        get_resp = await client.get(f"{API}/{company_id}", headers=headers)
        assert get_resp.status_code == 403

    async def test_non_owner_cannot_delete(
        self, client: AsyncClient, basic_user: dict, auth_headers
    ):
        """Admin (non-owner) should not be able to delete."""
        headers = auth_headers(basic_user["token"])
        create_resp = await client.post(
            f"{API}", headers=headers, json=_company_payload(mersis_number="DEL00002")
        )
        company_id = create_resp.json()["id"]

        # Invite a second user as admin
        from tests.conftest import _create_verified_user

        user2 = await _create_verified_user(
            client, email="admin2@dezztech.com", password="Admin2Pass1!"
        )
        await client.post(
            f"{API}/{company_id}/invite-user",
            headers=headers,
            json={"email": user2["email"], "role": "admin"},
        )

        # Accept invitation
        from sqlalchemy import select
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

        from tests.conftest import TEST_DATABASE_URL
        from src.domains.companies.models import CompanyInvitation

        engine = create_async_engine(TEST_DATABASE_URL, echo=False)
        factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with factory() as session:
            result = await session.execute(
                select(CompanyInvitation).where(
                    CompanyInvitation.email == user2["email"],
                    CompanyInvitation.is_accepted.is_(False),
                )
            )
            inv = result.scalar_one()
            token = inv.token
        await engine.dispose()

        await client.post(
            f"{API}/invitations/accept",
            json={"token": token},
        )

        # Admin tries to delete — should fail
        headers2 = auth_headers(user2["token"])
        resp = await client.delete(f"{API}/{company_id}", headers=headers2)
        assert resp.status_code == 403

    async def test_unauthenticated(self, client: AsyncClient):
        resp = await client.delete(f"{API}/{uuid.uuid4()}")
        assert resp.status_code == 401


class TestDeactivateActivateCompany:
    """PATCH /companies/{id}/deactivate and /activate"""

    async def test_deactivate_and_activate(
        self, client: AsyncClient, basic_user: dict, auth_headers
    ):
        headers = auth_headers(basic_user["token"])
        create_resp = await client.post(
            f"{API}", headers=headers, json=_company_payload(mersis_number="DEACT001")
        )
        company_id = create_resp.json()["id"]

        # Deactivate
        resp = await client.patch(f"{API}/{company_id}/deactivate", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["is_active"] is False

        # Activate
        resp = await client.patch(f"{API}/{company_id}/activate", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["is_active"] is True


class TestCompanySectors:
    """CRUD for /companies/{id}/sectors"""

    async def test_create_and_list(
        self, client: AsyncClient, basic_user: dict, auth_headers
    ):
        headers = auth_headers(basic_user["token"])
        create_resp = await client.post(
            f"{API}", headers=headers, json=_company_payload(mersis_number="SEC00001")
        )
        company_id = create_resp.json()["id"]

        # Create sector
        sector_resp = await client.post(
            f"{API}/{company_id}/sectors",
            headers=headers,
            json={"nace_code": "62.01", "nace_name": "Bilgisayar Programlama"},
        )
        assert sector_resp.status_code == 201
        sector_id = sector_resp.json()["id"]

        # List sectors
        list_resp = await client.get(f"{API}/{company_id}/sectors", headers=headers)
        assert list_resp.status_code == 200
        assert len(list_resp.json()) >= 1

        # Update sector brand
        update_resp = await client.patch(
            f"{API}/{company_id}/sectors/{sector_id}",
            headers=headers,
            json={"brand_name": "TechBrand"},
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["brand_name"] == "TechBrand"

        # Delete sector
        del_resp = await client.delete(
            f"{API}/{company_id}/sectors/{sector_id}", headers=headers
        )
        assert del_resp.status_code == 204

    async def test_duplicate_nace_code(
        self, client: AsyncClient, basic_user: dict, auth_headers
    ):
        headers = auth_headers(basic_user["token"])
        create_resp = await client.post(
            f"{API}", headers=headers, json=_company_payload(mersis_number="SEC00002")
        )
        company_id = create_resp.json()["id"]

        sector_data = {"nace_code": "62.02", "nace_name": "Bilisim Danismanligi"}
        await client.post(f"{API}/{company_id}/sectors", headers=headers, json=sector_data)
        resp = await client.post(f"{API}/{company_id}/sectors", headers=headers, json=sector_data)
        assert resp.status_code == 409


class TestCompanyMembers:
    """GET /companies/{id}/members"""

    async def test_list_members(
        self, client: AsyncClient, basic_user: dict, auth_headers
    ):
        headers = auth_headers(basic_user["token"])
        create_resp = await client.post(
            f"{API}", headers=headers, json=_company_payload(mersis_number="MEM00001")
        )
        company_id = create_resp.json()["id"]

        resp = await client.get(f"{API}/{company_id}/members", headers=headers)
        assert resp.status_code == 200
        members = resp.json()
        assert len(members) >= 1
        assert members[0]["role"] == "owner"


class TestInviteUser:
    """POST /companies/{id}/invite-user"""

    async def test_invite_success(
        self, client: AsyncClient, basic_user: dict, auth_headers
    ):
        headers = auth_headers(basic_user["token"])
        create_resp = await client.post(
            f"{API}", headers=headers, json=_company_payload(mersis_number="INV00001")
        )
        company_id = create_resp.json()["id"]

        resp = await client.post(
            f"{API}/{company_id}/invite-user",
            headers=headers,
            json={"email": "invited@company.com", "role": "viewer"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "invited@company.com"
        assert data["role"] == "viewer"
        assert data["is_accepted"] is False

    async def test_invite_invalid_role(
        self, client: AsyncClient, basic_user: dict, auth_headers
    ):
        headers = auth_headers(basic_user["token"])
        create_resp = await client.post(
            f"{API}", headers=headers, json=_company_payload(mersis_number="INV00002")
        )
        company_id = create_resp.json()["id"]

        resp = await client.post(
            f"{API}/{company_id}/invite-user",
            headers=headers,
            json={"email": "user@company.com", "role": "owner"},
        )
        assert resp.status_code == 400
        assert resp.json()["error_code"] == "INVALID_INVITATION_ROLE"

    async def test_invite_duplicate(
        self, client: AsyncClient, basic_user: dict, auth_headers
    ):
        headers = auth_headers(basic_user["token"])
        create_resp = await client.post(
            f"{API}", headers=headers, json=_company_payload(mersis_number="INV00003")
        )
        company_id = create_resp.json()["id"]

        await client.post(
            f"{API}/{company_id}/invite-user",
            headers=headers,
            json={"email": "dup@company.com", "role": "viewer"},
        )
        resp = await client.post(
            f"{API}/{company_id}/invite-user",
            headers=headers,
            json={"email": "dup@company.com", "role": "viewer"},
        )
        assert resp.status_code == 409
        assert resp.json()["error_code"] == "INVITATION_ALREADY_EXISTS"

    async def test_invite_existing_member(
        self, client: AsyncClient, basic_user: dict, auth_headers
    ):
        """Can't invite someone who's already a member."""
        headers = auth_headers(basic_user["token"])
        create_resp = await client.post(
            f"{API}", headers=headers, json=_company_payload(mersis_number="INV00004")
        )
        company_id = create_resp.json()["id"]

        # The creator (registered_user) is already a member as owner
        resp = await client.post(
            f"{API}/{company_id}/invite-user",
            headers=headers,
            json={"email": basic_user["email"], "role": "viewer"},
        )
        assert resp.status_code == 409
        assert resp.json()["error_code"] == "USER_ALREADY_MEMBER"

    async def test_consultant_requires_admin(
        self, client: AsyncClient, basic_user: dict, auth_headers
    ):
        """Consultant role requires the invitee to have Admin system role."""
        headers = auth_headers(basic_user["token"])
        create_resp = await client.post(
            f"{API}", headers=headers, json=_company_payload(mersis_number="INV00005")
        )
        company_id = create_resp.json()["id"]

        # invited@notadmin.com is not registered — so not an admin
        resp = await client.post(
            f"{API}/{company_id}/invite-user",
            headers=headers,
            json={"email": "invited@notadmin.com", "role": "consultant"},
        )
        assert resp.status_code == 403
        assert resp.json()["error_code"] == "CONSULTANT_REQUIRES_ADMIN"

    async def test_unauthenticated(self, client: AsyncClient):
        resp = await client.post(
            f"{API}/{uuid.uuid4()}/invite-user",
            json={"email": "user@company.com", "role": "viewer"},
        )
        assert resp.status_code == 401


class TestAcceptInvitation:
    """POST /companies/invitations/accept"""

    async def _create_invitation(
        self, client: AsyncClient, headers: dict, mersis: str, email: str, role: str = "viewer"
    ) -> tuple[str, str]:
        """Helper: create company + invite. Returns (company_id, token)."""
        from sqlalchemy import select
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

        from tests.conftest import TEST_DATABASE_URL
        from src.domains.companies.models import CompanyInvitation

        create_resp = await client.post(
            f"{API}", headers=headers, json=_company_payload(mersis_number=mersis)
        )
        company_id = create_resp.json()["id"]

        await client.post(
            f"{API}/{company_id}/invite-user",
            headers=headers,
            json={"email": email, "role": role},
        )

        # Get token from DB
        engine = create_async_engine(TEST_DATABASE_URL, echo=False)
        factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with factory() as session:
            result = await session.execute(
                select(CompanyInvitation).where(
                    CompanyInvitation.email == email,
                    CompanyInvitation.is_accepted.is_(False),
                )
            )
            inv = result.scalar_one()
            token = inv.token
        await engine.dispose()

        return company_id, token

    async def test_accept_new_user(
        self, client: AsyncClient, basic_user: dict, auth_headers
    ):
        headers = auth_headers(basic_user["token"])
        company_id, token = await self._create_invitation(
            client, headers, "ACC00001", "newguy@company.com"
        )

        resp = await client.post(
            f"{API}/invitations/accept",
            json={
                "token": token,
                "first_name": "New",
                "last_name": "Guy",
                "password": "NewGuy1234!",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["accepted"] is True
        assert data["is_new_user"] is True

    async def test_accept_existing_user(
        self, client: AsyncClient, basic_user: dict, auth_headers
    ):
        """Invite an already-registered user who is not yet a member."""
        headers = auth_headers(basic_user["token"])

        # Register a second user
        from tests.conftest import _create_verified_user

        user2 = await _create_verified_user(
            client, email="user2@dezztech.com", password="User2Pass1!"
        )

        company_id, token = await self._create_invitation(
            client, headers, "ACC00002", user2["email"]
        )

        resp = await client.post(
            f"{API}/invitations/accept",
            json={"token": token},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["accepted"] is True
        assert data["is_new_user"] is False

    async def test_accept_invalid_token(self, client: AsyncClient):
        resp = await client.post(
            f"{API}/invitations/accept",
            json={"token": "nonexistent-token"},
        )
        assert resp.status_code == 400
        assert resp.json()["error_code"] == "INVALID_INVITATION"

    async def test_accept_twice(
        self, client: AsyncClient, basic_user: dict, auth_headers
    ):
        headers = auth_headers(basic_user["token"])
        _, token = await self._create_invitation(
            client, headers, "ACC00003", "twice@company.com"
        )

        # Accept first time
        await client.post(
            f"{API}/invitations/accept",
            json={"token": token, "first_name": "T", "last_name": "W"},
        )

        # Accept again
        resp = await client.post(
            f"{API}/invitations/accept",
            json={"token": token},
        )
        assert resp.status_code == 400
        assert resp.json()["error_code"] == "INVALID_INVITATION"

    async def test_new_user_missing_name(
        self, client: AsyncClient, basic_user: dict, auth_headers
    ):
        headers = auth_headers(basic_user["token"])
        _, token = await self._create_invitation(
            client, headers, "ACC00004", "noname@company.com"
        )

        resp = await client.post(
            f"{API}/invitations/accept",
            json={"token": token},
        )
        assert resp.status_code == 400
