import uuid
from datetime import date
from typing import Optional

from sqlalchemy import Boolean, Date, Enum, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.core.models import TimestampMixin
from src.domains.subscriptions.constants import PLAN_DEFINITIONS, PlanTier


class UserSubscription(Base, TimestampMixin):
    """User's active subscription with plan tier and extra quotas.

    Each user has exactly one subscription record.
    Freemium is assigned on registration.
    """

    __tablename__ = "user_subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    plan: Mapped[PlanTier] = mapped_column(
        Enum(PlanTier, name="plan_tier", values_callable=lambda e: [x.value for x in e]),
        nullable=False,
        default=PlanTier.FREEMIUM,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Billing period (nullable for freemium)
    billing_cycle: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )  # "monthly" or "yearly"
    current_period_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    current_period_end: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # À la carte extra quotas (PRD 4.2)
    extra_company_quota: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    extra_product_quota_per_company: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    extra_member_quota_per_company: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="subscription", lazy="selectin")

    # ── Computed limits ──

    @property
    def plan_definition(self) -> dict:
        """Get the plan definition for this subscription's tier."""
        return PLAN_DEFINITIONS[self.plan]

    @property
    def max_companies(self) -> int:
        """Maximum companies this user can own (plan + extra quota)."""
        return self.plan_definition["max_companies"] + self.extra_company_quota

    @property
    def max_products_per_company(self) -> int:
        """Maximum products per company (plan + extra quota)."""
        return self.plan_definition["max_products_per_company"] + self.extra_product_quota_per_company

    @property
    def max_members_per_company(self) -> int:
        """Maximum members per company (plan + extra quota)."""
        return self.plan_definition["max_members_per_company"] + self.extra_member_quota_per_company

    @property
    def can_create_company(self) -> bool:
        return self.plan_definition["can_create_company"]

    @property
    def can_apply(self) -> bool:
        return self.plan_definition["can_apply"]
