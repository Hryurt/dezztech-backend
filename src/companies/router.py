import uuid

from fastapi import APIRouter, Depends, status

from src.auth.dependencies import get_current_user
from src.companies.config import DEFAULT_COMPANY_PAGE_SIZE
from src.companies.dependencies import (
    get_company_service,
    require_company_admin_or_owner,
    require_company_member,
)
from src.companies.models import UserCompany
from src.companies.schemas import (
    CompanyCreateRequest,
    CompanyMemberListItem,
    CompanyResponse,
    CompanySectorCreateRequest,
    CompanySectorResponse,
    CompanySectorUpdateRequest,
    CompanyUpdateRequest,
    MyCompanyListItem,
    PaginatedCompanyListResponse,
)
from src.companies.service import CompanyService
from src.users.models import User

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.post(
    "",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_company(
    data: CompanyCreateRequest,
    current_user: User = Depends(get_current_user),
    company_service: CompanyService = Depends(get_company_service),
) -> CompanyResponse:
    """Create a new company."""
    company = await company_service.create_company(
        user_id=current_user.id,
        data=data,
    )
    return CompanyResponse.model_validate(company)


@router.get(
    "/my",
    response_model=PaginatedCompanyListResponse,
)
async def list_my_companies(
    current_user: User = Depends(get_current_user),
    company_service: CompanyService = Depends(get_company_service),
    page: int = 1,
    limit: int = DEFAULT_COMPANY_PAGE_SIZE,
    search: str | None = None,
) -> PaginatedCompanyListResponse:
    """List companies for the current user."""
    items, total = await company_service.list_my_companies(
        current_user, page, limit, search
    )
    return PaginatedCompanyListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
    )


@router.get(
    "/{company_id}",
    response_model=CompanyResponse,
)
async def get_company(
    company_id: uuid.UUID,
    user_company: UserCompany = Depends(require_company_member),
    company_service: CompanyService = Depends(get_company_service),
) -> CompanyResponse:
    """Get a company by ID."""
    user_id = user_company.user_id
    company = await company_service.get_company_by_id(company_id, user_id=user_id)
    return CompanyResponse.model_validate(company)


@router.patch(
    "/{company_id}",
    response_model=CompanyResponse,
)
async def update_company(
    company_id: uuid.UUID,
    data: CompanyUpdateRequest,
    user_company: UserCompany = Depends(require_company_admin_or_owner),
    company_service: CompanyService = Depends(get_company_service),
) -> CompanyResponse:
    """Update company core fields."""
    user_id = user_company.user_id
    company = await company_service.update_company(
        company_id, data, user_id=user_id
    )
    return CompanyResponse.model_validate(company)


@router.patch(
    "/{company_id}/deactivate",
    response_model=CompanyResponse,
)
async def deactivate_company(
    company_id: uuid.UUID,
    user_company: UserCompany = Depends(require_company_admin_or_owner),
    company_service: CompanyService = Depends(get_company_service),
) -> CompanyResponse:
    """Deactivate a company."""
    user_id = user_company.user_id
    company = await company_service.deactivate_company(
        company_id, user_id=user_id
    )
    return CompanyResponse.model_validate(company)


@router.patch(
    "/{company_id}/activate",
    response_model=CompanyResponse,
)
async def activate_company(
    company_id: uuid.UUID,
    user_company: UserCompany = Depends(require_company_admin_or_owner),
    company_service: CompanyService = Depends(get_company_service),
) -> CompanyResponse:
    """Activate a company."""
    user_id = user_company.user_id
    company = await company_service.activate_company(
        company_id, user_id=user_id
    )
    return CompanyResponse.model_validate(company)


@router.get(
    "/{company_id}/members",
    response_model=list[CompanyMemberListItem],
)
async def list_company_members(
    company_id: uuid.UUID,
    user_company: UserCompany = Depends(require_company_admin_or_owner),
    company_service: CompanyService = Depends(get_company_service),
) -> list[CompanyMemberListItem]:
    """List members of a company."""
    user_id = user_company.user_id
    return await company_service.list_company_members(
        company_id, user_id=user_id
    )


@router.get(
    "/{company_id}/sectors",
    response_model=list[CompanySectorResponse],
)
async def list_company_sectors(
    company_id: uuid.UUID,
    user_company: UserCompany = Depends(require_company_member),
    company_service: CompanyService = Depends(get_company_service),
) -> list[CompanySectorResponse]:
    """List sectors of a company."""
    sectors = await company_service.list_company_sectors(company_id)
    return [CompanySectorResponse.model_validate(sector) for sector in sectors]


@router.post(
    "/{company_id}/sectors",
    response_model=CompanySectorResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_company_sector(
    company_id: uuid.UUID,
    data: CompanySectorCreateRequest,
    user_company: UserCompany = Depends(require_company_admin_or_owner),
    company_service: CompanyService = Depends(get_company_service),
) -> CompanySectorResponse:
    """Create a new sector for a company."""
    user_id = user_company.user_id
    sector = await company_service.create_company_sector(
        company_id, data, user_id=user_id
    )
    return CompanySectorResponse.model_validate(sector)


@router.delete(
    "/{company_id}/sectors/{sector_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_company_sector(
    company_id: uuid.UUID,
    sector_id: uuid.UUID,
    user_company: UserCompany = Depends(require_company_admin_or_owner),
    company_service: CompanyService = Depends(get_company_service),
) -> None:
    """Delete a sector from a company."""
    user_id = user_company.user_id
    await company_service.delete_company_sector(
        company_id, sector_id, user_id=user_id
    )


@router.patch(
    "/{company_id}/sectors/{sector_id}",
    response_model=CompanySectorResponse,
)
async def update_company_sector(
    company_id: uuid.UUID,
    sector_id: uuid.UUID,
    data: CompanySectorUpdateRequest,
    user_company: UserCompany = Depends(require_company_admin_or_owner),
    company_service: CompanyService = Depends(get_company_service),
) -> CompanySectorResponse:
    """Update a sector's brand name."""
    user_id = user_company.user_id
    sector = await company_service.update_company_sector_brand(
        company_id, sector_id, data.brand_name, user_id=user_id
    )
    return CompanySectorResponse.model_validate(sector)


@router.post("/{company_id}/invite-user")
async def invite_user(
    company_id: uuid.UUID,
    user_company: UserCompany = Depends(require_company_admin_or_owner),
):
    """Invite a user to the company (placeholder)."""
    return {
        "message": "User invitation endpoint accessed successfully",
        "company_id": company_id,
        "acting_role": user_company.role.name,
    }
