import uuid

from fastapi import APIRouter, Depends, status

from src.domains.auth.dependencies import get_current_user, require_superuser
from src.domains.subscriptions.dependencies import get_subscription_service
from src.domains.subscriptions.schemas import (
    ChangePlanRequest,
    SubscriptionResponse,
    UpdateExtraQuotasRequest,
)
from src.domains.subscriptions.service import SubscriptionService
from src.domains.users.models import User

router = APIRouter()


@router.get(
    "/me",
    response_model=SubscriptionResponse,
)
async def get_my_subscription(
    current_user: User = Depends(get_current_user),
    service: SubscriptionService = Depends(get_subscription_service),
) -> SubscriptionResponse:
    """Get current user's subscription details."""
    sub = await service.get_subscription(current_user.id)
    return SubscriptionResponse.model_validate(sub)


@router.get(
    "/{user_id}",
    response_model=SubscriptionResponse,
)
async def get_user_subscription(
    user_id: uuid.UUID,
    _admin: User = Depends(require_superuser),
    service: SubscriptionService = Depends(get_subscription_service),
) -> SubscriptionResponse:
    """Get a user's subscription details (Super Admin only)."""
    sub = await service.get_subscription(user_id)
    return SubscriptionResponse.model_validate(sub)


@router.put(
    "/change-plan",
    response_model=SubscriptionResponse,
)
async def change_plan(
    data: ChangePlanRequest,
    _admin: User = Depends(require_superuser),
    service: SubscriptionService = Depends(get_subscription_service),
) -> SubscriptionResponse:
    """Change a user's subscription plan (Super Admin only)."""
    sub = await service.change_plan(data.user_id, data.plan)
    return SubscriptionResponse.model_validate(sub)


@router.put(
    "/extra-quotas",
    response_model=SubscriptionResponse,
)
async def update_extra_quotas(
    data: UpdateExtraQuotasRequest,
    _admin: User = Depends(require_superuser),
    service: SubscriptionService = Depends(get_subscription_service),
) -> SubscriptionResponse:
    """Update à la carte extra quotas (Super Admin only)."""
    sub = await service.update_extra_quotas(
        data.user_id,
        extra_company_quota=data.extra_company_quota,
        extra_product_quota_per_company=data.extra_product_quota_per_company,
        extra_member_quota_per_company=data.extra_member_quota_per_company,
    )
    return SubscriptionResponse.model_validate(sub)
