"""Integration tests for subscription system and limit enforcement."""

from httpx import AsyncClient

from tests.conftest import _create_verified_user, _upgrade_plan

COMPANIES_API = "/api/v1/companies"
SUBS_API = "/api/v1/subscriptions"


def _company_payload(**overrides) -> dict:
    base = {
        "name": "Test Co",
        "mersis_number": "1234567890123456",
        "tax_number": "1234567890",
        "tax_office": "Istanbul",
        "employee_count": 5,
    }
    base.update(overrides)
    return base


class TestFreemiumOnRegistration:
    """New users should automatically get freemium subscription."""

    async def test_register_creates_freemium(
        self, client: AsyncClient, registered_user: dict, auth_headers
    ):
        headers = auth_headers(registered_user["token"])
        resp = await client.get(f"{SUBS_API}/me", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["plan"] == "freemium"
        assert data["is_active"] is True
        assert data["max_companies"] == 0
        assert data["can_create_company"] is False


class TestFreemiumLimits:
    """Freemium users cannot create companies."""

    async def test_cannot_create_company(
        self, client: AsyncClient, registered_user: dict, auth_headers
    ):
        headers = auth_headers(registered_user["token"])
        resp = await client.post(
            COMPANIES_API,
            headers=headers,
            json=_company_payload(mersis_number="FREE0001"),
        )
        assert resp.status_code == 403
        assert resp.json()["error_code"] == "FREEMIUM_CANNOT_CREATE_COMPANY"


class TestBasicPlanLimits:
    """Basic plan: 1 company, 3 members per company."""

    async def test_can_create_one_company(self, client: AsyncClient, auth_headers):
        user = await _create_verified_user(client, email="basic@dezztech.com")
        await _upgrade_plan(user["user_id"], "basic")
        headers = auth_headers(user["token"])

        resp1 = await client.post(
            COMPANIES_API, headers=headers, json=_company_payload(mersis_number="BAS00001")
        )
        assert resp1.status_code == 201

        resp2 = await client.post(
            COMPANIES_API, headers=headers, json=_company_payload(mersis_number="BAS00002")
        )
        assert resp2.status_code == 403
        assert resp2.json()["error_code"] == "COMPANY_LIMIT_REACHED"

    async def test_member_limit(self, client: AsyncClient, auth_headers):
        """Basic plan allows 3 members. Owner(1) + 2 invites = 3 = limit. 3rd invite fails."""
        user = await _create_verified_user(client, email="basicmem@dezztech.com")
        await _upgrade_plan(user["user_id"], "basic")
        headers = auth_headers(user["token"])

        create_resp = await client.post(
            COMPANIES_API, headers=headers, json=_company_payload(mersis_number="BASM0001")
        )
        assert create_resp.status_code == 201
        company_id = create_resp.json()["id"]

        resp1 = await client.post(
            f"{COMPANIES_API}/{company_id}/invite-user",
            headers=headers,
            json={"email": "mem1@company.com", "role": "viewer"},
        )
        assert resp1.status_code == 201

        resp2 = await client.post(
            f"{COMPANIES_API}/{company_id}/invite-user",
            headers=headers,
            json={"email": "mem2@company.com", "role": "viewer"},
        )
        assert resp2.status_code == 201

        resp3 = await client.post(
            f"{COMPANIES_API}/{company_id}/invite-user",
            headers=headers,
            json={"email": "mem3@company.com", "role": "viewer"},
        )
        assert resp3.status_code == 403
        assert resp3.json()["error_code"] == "MEMBER_LIMIT_REACHED"


class TestExtraQuotas:
    """Extra quotas should increase limits."""

    async def test_extra_company_quota(self, client: AsyncClient, auth_headers):
        user = await _create_verified_user(client, email="extra@dezztech.com")
        await _upgrade_plan(user["user_id"], "basic")
        headers = auth_headers(user["token"])

        # Add 1 extra company quota
        from sqlalchemy import select
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

        from src.domains.subscriptions.models import UserSubscription
        from tests.conftest import TEST_DATABASE_URL

        engine = create_async_engine(TEST_DATABASE_URL, echo=False)
        factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with factory() as session:
            result = await session.execute(
                select(UserSubscription).where(
                    UserSubscription.user_id == user["user_id"]
                )
            )
            sub = result.scalar_one()
            sub.extra_company_quota = 1
            await session.commit()
        await engine.dispose()

        resp1 = await client.post(
            COMPANIES_API, headers=headers, json=_company_payload(mersis_number="EXT00001")
        )
        assert resp1.status_code == 201

        resp2 = await client.post(
            COMPANIES_API, headers=headers, json=_company_payload(mersis_number="EXT00002")
        )
        assert resp2.status_code == 201

        resp3 = await client.post(
            COMPANIES_API, headers=headers, json=_company_payload(mersis_number="EXT00003")
        )
        assert resp3.status_code == 403


class TestProPlanLimits:
    """Pro plan: 2 companies."""

    async def test_can_create_two_companies(self, client: AsyncClient, auth_headers):
        user = await _create_verified_user(client, email="pro@dezztech.com")
        await _upgrade_plan(user["user_id"], "pro")
        headers = auth_headers(user["token"])

        resp1 = await client.post(
            COMPANIES_API, headers=headers, json=_company_payload(mersis_number="PRO00001")
        )
        assert resp1.status_code == 201

        resp2 = await client.post(
            COMPANIES_API, headers=headers, json=_company_payload(mersis_number="PRO00002")
        )
        assert resp2.status_code == 201

        resp3 = await client.post(
            COMPANIES_API, headers=headers, json=_company_payload(mersis_number="PRO00003")
        )
        assert resp3.status_code == 403


class TestSubscriptionEndpoints:
    """Subscription API endpoints."""

    async def test_get_my_subscription(
        self, client: AsyncClient, registered_user: dict, auth_headers
    ):
        headers = auth_headers(registered_user["token"])
        resp = await client.get(f"{SUBS_API}/me", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "plan" in data
        assert "max_companies" in data
        assert "can_create_company" in data

    async def test_unauthenticated(self, client: AsyncClient):
        resp = await client.get(f"{SUBS_API}/me")
        assert resp.status_code == 401
