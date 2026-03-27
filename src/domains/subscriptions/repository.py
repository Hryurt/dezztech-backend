import uuid
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.subscriptions.constants import PlanTier
from src.domains.subscriptions.models import UserSubscription


class SubscriptionRepository:
    """Repository for subscription database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(self, user_id: uuid.UUID) -> Optional[UserSubscription]:
        """Get subscription for a user."""
        result = await self.db.execute(
            select(UserSubscription).where(UserSubscription.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: uuid.UUID, plan: PlanTier = PlanTier.FREEMIUM) -> UserSubscription:
        """Create a subscription for a user."""
        subscription = UserSubscription(user_id=user_id, plan=plan)
        self.db.add(subscription)
        return subscription

    async def count_user_owned_companies(self, user_id: uuid.UUID) -> int:
        """Count companies where user is the owner."""
        from src.domains.companies.models import CompanyRole, UserCompany

        stmt = (
            select(func.count())
            .select_from(UserCompany)
            .join(CompanyRole, UserCompany.role_id == CompanyRole.id)
            .where(
                UserCompany.user_id == user_id,
                UserCompany.is_active.is_(True),
                CompanyRole.name == "owner",
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def count_company_members_and_pending(self, company_id: uuid.UUID) -> int:
        """Count active members + pending invitations for a company."""
        from src.domains.companies.models import CompanyInvitation, UserCompany

        # Active members
        member_stmt = (
            select(func.count())
            .select_from(UserCompany)
            .where(
                UserCompany.company_id == company_id,
                UserCompany.is_active.is_(True),
            )
        )
        member_result = await self.db.execute(member_stmt)
        member_count = member_result.scalar() or 0

        # Pending invitations (not accepted, not expired)
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        invite_stmt = (
            select(func.count())
            .select_from(CompanyInvitation)
            .where(
                CompanyInvitation.company_id == company_id,
                CompanyInvitation.is_accepted.is_(False),
                CompanyInvitation.expires_at > now,
            )
        )
        invite_result = await self.db.execute(invite_stmt)
        invite_count = invite_result.scalar() or 0

        return member_count + invite_count

    async def get_company_owner_id(self, company_id: uuid.UUID) -> uuid.UUID | None:
        """Get the owner user_id for a company."""
        from src.domains.companies.models import CompanyRole, UserCompany

        stmt = (
            select(UserCompany.user_id)
            .join(CompanyRole, UserCompany.role_id == CompanyRole.id)
            .where(
                UserCompany.company_id == company_id,
                UserCompany.is_active.is_(True),
                CompanyRole.name == "owner",
            )
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
