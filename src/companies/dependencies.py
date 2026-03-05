import uuid

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.companies.constants import COMPANY_MANAGE_ROLES, COMPANY_OWNER_ROLE
from src.companies.models import CompanyRole, UserCompany
from src.companies.service import CompanyService
from src.database import get_db
from src.users.models import User, UserRole


async def _get_active_membership(
    company_id: uuid.UUID,
    current_user: User,
    db: AsyncSession,
    *,
    not_member_detail: str = "You do not have permission to access this company.",
) -> UserCompany:
    """Get active UserCompany membership for user in company.

    SUPER_ADMIN receives a synthetic UserCompany. Raises 403 if user is not an active member.
    """
    if current_user.role == UserRole.SUPER_ADMIN:
        owner_role = await CompanyRole.get_by_name(db, COMPANY_OWNER_ROLE)
        if owner_role is None:
            raise RuntimeError(
                f"Company role '{COMPANY_OWNER_ROLE}' not found. Seed roles via migration."
            )
        user_company = UserCompany(
            user_id=current_user.id,
            company_id=company_id,
            role_id=owner_role.id,
            is_active=True,
        )
        user_company.role = owner_role
        return user_company

    stmt = select(UserCompany).where(
        UserCompany.user_id == current_user.id,
        UserCompany.company_id == company_id,
        UserCompany.is_active.is_(True),
    )
    result = await db.execute(stmt)
    user_company = result.scalar_one_or_none()
    if user_company is None:
        raise HTTPException(status_code=403, detail=not_member_detail)
    return user_company


async def require_company_member(
    company_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserCompany:
    """Ensure the current user is an active member of the given company.

    SUPER_ADMIN receives a synthetic UserCompany with owner-equivalent access.

    Args:
        company_id: Company ID
        current_user: Authenticated user
        db: Database session

    Returns:
        UserCompany record (real or synthetic for SUPER_ADMIN)

    Raises:
        HTTPException: 403 if user is not a member
    """
    return await _get_active_membership(company_id, current_user, db)


async def require_company_admin_or_owner(
    company_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserCompany:
    """Ensure the current user has owner or admin role in the given company.

    SUPER_ADMIN receives a synthetic UserCompany with owner-equivalent access.

    Args:
        company_id: Company ID
        current_user: Authenticated user
        db: Database session

    Returns:
        UserCompany record (real or synthetic for SUPER_ADMIN)

    Raises:
        HTTPException: 403 if user lacks permission
    """
    user_company = await _get_active_membership(
        company_id,
        current_user,
        db,
        not_member_detail="You do not have permission to manage this company.",
    )

    role = user_company.role
    if role is None or role.name not in COMPANY_MANAGE_ROLES:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to manage this company.",
        )

    return user_company


def get_company_service(db: AsyncSession = Depends(get_db)) -> CompanyService:
    """Factory function for CompanyService.

    Args:
        db: Database session

    Returns:
        CompanyService instance
    """
    return CompanyService(db)
