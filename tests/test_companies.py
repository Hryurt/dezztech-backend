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

    async def test_success(self, client: AsyncClient, registered_user: dict, auth_headers):
        headers = auth_headers(registered_user["token"])
        resp = await client.post(f"{API}", headers=headers, json=_company_payload())
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Test Sirket A.S."
        assert data["is_active"] is True

    async def test_duplicate_mersis(self, client: AsyncClient, registered_user: dict, auth_headers):
        headers = auth_headers(registered_user["token"])
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

    async def test_success(self, client: AsyncClient, registered_user: dict, auth_headers):
        headers = auth_headers(registered_user["token"])
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

    async def test_success(self, client: AsyncClient, registered_user: dict, auth_headers):
        headers = auth_headers(registered_user["token"])
        create_resp = await client.post(
            f"{API}", headers=headers, json=_company_payload(mersis_number="GET00001")
        )
        company_id = create_resp.json()["id"]

        resp = await client.get(f"{API}/{company_id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == company_id

    async def test_not_member(self, client: AsyncClient, registered_user: dict, auth_headers):
        headers = auth_headers(registered_user["token"])
        fake_id = str(uuid.uuid4())
        resp = await client.get(f"{API}/{fake_id}", headers=headers)
        assert resp.status_code == 403


class TestUpdateCompany:
    """PATCH /companies/{id}"""

    async def test_success(self, client: AsyncClient, registered_user: dict, auth_headers):
        headers = auth_headers(registered_user["token"])
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


class TestDeactivateActivateCompany:
    """PATCH /companies/{id}/deactivate and /activate"""

    async def test_deactivate_and_activate(
        self, client: AsyncClient, registered_user: dict, auth_headers
    ):
        headers = auth_headers(registered_user["token"])
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
        self, client: AsyncClient, registered_user: dict, auth_headers
    ):
        headers = auth_headers(registered_user["token"])
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
        self, client: AsyncClient, registered_user: dict, auth_headers
    ):
        headers = auth_headers(registered_user["token"])
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
        self, client: AsyncClient, registered_user: dict, auth_headers
    ):
        headers = auth_headers(registered_user["token"])
        create_resp = await client.post(
            f"{API}", headers=headers, json=_company_payload(mersis_number="MEM00001")
        )
        company_id = create_resp.json()["id"]

        resp = await client.get(f"{API}/{company_id}/members", headers=headers)
        assert resp.status_code == 200
        members = resp.json()
        assert len(members) >= 1
        assert members[0]["role"] == "owner"
