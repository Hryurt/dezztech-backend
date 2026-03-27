import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logger import get_logger
from src.domains.subscriptions.constants import PlanTier
from src.domains.subscriptions.exceptions import (
    CompanyLimitReachedException,
    FreemiumCannotCreateCompanyException,
    MemberLimitReachedException,
    SubscriptionNotFoundException,
)
from src.domains.subscriptions.models import UserSubscription
from src.domains.subscriptions.repository import SubscriptionRepository

logger = get_logger(__name__)


class SubscriptionService:
    """Service for subscription operations and limit enforcement."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SubscriptionRepository(db)

    async def create_freemium(self, user_id: uuid.UUID) -> UserSubscription:
        """Create a freemium subscription for a new user."""
        subscription = await self.repo.create(user_id, PlanTier.FREEMIUM)
        return subscription

    async def get_subscription(self, user_id: uuid.UUID) -> UserSubscription:
        """Get user's subscription, raise if not found."""
        sub = await self.repo.get_by_user_id(user_id)
        if sub is None:
            raise SubscriptionNotFoundException()
        return sub

    async def change_plan(
        self,
        user_id: uuid.UUID,
        new_plan: PlanTier,
    ) -> UserSubscription:
        """Change a user's subscription plan (Super Admin action).

        Args:
            user_id: User ID
            new_plan: New plan tier

        Returns:
            Updated subscription
        """
        sub = await self.get_subscription(user_id)
        old_plan = sub.plan
        sub.plan = new_plan
        await self.db.commit()
        await self.db.refresh(sub)

        logger.info(
            "Subscription plan changed",
            extra={
                "user_id": str(user_id),
                "old_plan": old_plan.value,
                "new_plan": new_plan.value,
            },
        )
        return sub

    async def update_extra_quotas(
        self,
        user_id: uuid.UUID,
        *,
        extra_company_quota: int | None = None,
        extra_product_quota_per_company: int | None = None,
        extra_member_quota_per_company: int | None = None,
    ) -> UserSubscription:
        """Update à la carte extra quotas (Super Admin action)."""
        sub = await self.get_subscription(user_id)

        if extra_company_quota is not None:
            sub.extra_company_quota = extra_company_quota
        if extra_product_quota_per_company is not None:
            sub.extra_product_quota_per_company = extra_product_quota_per_company
        if extra_member_quota_per_company is not None:
            sub.extra_member_quota_per_company = extra_member_quota_per_company

        await self.db.commit()
        await self.db.refresh(sub)
        return sub

    # ── Limit enforcement ──

    async def enforce_company_creation_limit(self, user_id: uuid.UUID) -> None:
        """Check if user can create a new company.

        Raises:
            FreemiumCannotCreateCompanyException: If freemium
            CompanyLimitReachedException: If limit reached
        """
        sub = await self.get_subscription(user_id)

        if not sub.can_create_company:
            raise FreemiumCannotCreateCompanyException()

        current_count = await self.repo.count_user_owned_companies(user_id)
        if current_count >= sub.max_companies:
            raise CompanyLimitReachedException(max_companies=sub.max_companies)

    async def enforce_member_limit(
        self,
        company_owner_id: uuid.UUID,
        company_id: uuid.UUID,
    ) -> None:
        """Check if a company can accept a new member.

        Uses the company OWNER's subscription to determine limits.

        Raises:
            MemberLimitReachedException: If limit reached
        """
        sub = await self.get_subscription(company_owner_id)
        current_count = await self.repo.count_company_members_and_pending(company_id)
        if current_count >= sub.max_members_per_company:
            raise MemberLimitReachedException(
                max_members=sub.max_members_per_company
            )
