import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from src.domains.subscriptions.constants import PlanTier


class SubscriptionResponse(BaseModel):
    """Response schema for user subscription."""

    id: uuid.UUID
    user_id: uuid.UUID
    plan: PlanTier
    is_active: bool
    billing_cycle: str | None
    current_period_start: date | None
    current_period_end: date | None
    extra_company_quota: int
    extra_product_quota_per_company: int
    extra_member_quota_per_company: int
    # Computed limits
    max_companies: int
    max_products_per_company: int
    max_members_per_company: int
    can_create_company: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChangePlanRequest(BaseModel):
    """Request schema for changing a user's plan (Super Admin)."""

    user_id: uuid.UUID
    plan: PlanTier


class UpdateExtraQuotasRequest(BaseModel):
    """Request schema for updating extra quotas (Super Admin)."""

    user_id: uuid.UUID
    extra_company_quota: int | None = Field(None, ge=0)
    extra_product_quota_per_company: int | None = Field(None, ge=0)
    extra_member_quota_per_company: int | None = Field(None, ge=0)
