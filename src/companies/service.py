import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.companies.constants import COMPANY_OWNER_ROLE
from src.companies.exceptions import (
    CompanyMersisConflictException,
    CompanyNotFoundException,
    CompanySectorConflictException,
    CompanySectorNotFoundException,
)
from src.companies.models import (
    Company,
    CompanyRole,
    CompanySector,
    UserCompany,
)
from src.companies.schemas import (
    CompanyCreateRequest,
    CompanyMemberListItem,
    CompanySectorCreateRequest,
    CompanyUpdateRequest,
    MyCompanyListItem,
)
from src.companies.utils import normalize_iban, normalize_pagination, normalize_search
from src.users.models import User
from src.logger import get_logger

logger = get_logger(__name__)


class CompanyService:
    """Service for company operations."""

    def __init__(self, db: AsyncSession):
        """Initialize CompanyService with database session.

        Args:
            db: Database session
        """
        self.db = db

    async def _ensure_user_membership(
        self,
        *,
        user_id: uuid.UUID,
        company_id: uuid.UUID,
    ) -> None:
        """Ensure the user is a member of the company."""
        exists = await UserCompany.exists_for_user_and_company(
            self.db,
            user_id=user_id,
            company_id=company_id,
        )
        if not exists:
            raise CompanyNotFoundException(company_id=company_id)

    async def create_company(
        self,
        *,
        user_id: uuid.UUID,
        data: CompanyCreateRequest,
    ) -> Company:
        """Create a new company and assign the creating user as owner.

        Args:
            user_id: ID of the user creating the company (becomes owner)
            data: Company creation data

        Returns:
            Created company

        Raises:
            CompanyMersisConflictException: If MERSIS number already exists
        """
        # NOTE:
        # This check prevents most duplicates but the database must also
        # enforce a UNIQUE constraint on mersis_number to prevent race conditions.
        if await Company.exists_by_mersis(self.db, data.mersis_number):
            raise CompanyMersisConflictException(mersis_number=data.mersis_number)

        iban_try = normalize_iban(data.iban_try) if data.iban_try else None

        company = await Company.create(
            self.db,
            name=data.name,
            mersis_number=data.mersis_number,
            tax_number=data.tax_number,
            tax_office=data.tax_office,
            employee_count=data.employee_count,
        )

        company.foundation_date = data.foundation_date
        company.headquarters_address = data.headquarters_address
        company.iban_try = iban_try
        company.nace_code = data.nace_code
        company.activity_sector = data.activity_sector
        company.exporter_union = data.exporter_union
        company.hib_member_no = data.hib_member_no
        company.contact_full_name = data.contact_full_name
        company.contact_phone = data.contact_phone
        company.email = data.email
        company.phone = data.phone
        company.website = data.website
        company.kep_address = data.kep_address

        owner_role = await CompanyRole.get_by_name(self.db, COMPANY_OWNER_ROLE)
        if owner_role is None:
            raise RuntimeError(
                f"Company role '{COMPANY_OWNER_ROLE}' not found. Seed roles via migration."
            )

        await UserCompany.create_for_company(
            self.db,
            user_id=user_id,
            company_id=company.id,
            role_id=owner_role.id,
        )

        await self.db.commit()
        await self.db.refresh(company)

        logger.info(
            "Company created",
            extra={"company_id": str(company.id), "company_name": company.name},
        )
        return company

    async def get_company_by_id(
        self, company_id: uuid.UUID, user_id: uuid.UUID | None = None
    ) -> Company:
        """Get a company by ID.

        Args:
            company_id: Company ID
            user_id: Optional user ID for membership verification

        Returns:
            Company

        Raises:
            CompanyNotFoundException: If company not found
        """
        if user_id is not None:
            await self._ensure_user_membership(
                user_id=user_id,
                company_id=company_id,
            )
        company = await Company.get_by_id(self.db, company_id)

        if not company:
            raise CompanyNotFoundException(company_id=company_id)

        return company

    async def update_company(
        self,
        company_id: uuid.UUID,
        data: CompanyUpdateRequest,
        user_id: uuid.UUID | None = None,
    ) -> Company:
        """Update company fields. Only active companies can be updated.

        Args:
            company_id: Company ID
            data: Update data (partial)
            user_id: Optional user ID for membership verification

        Returns:
            Updated company

        Raises:
            CompanyNotFoundException: If company not found or not active
        """
        if user_id is not None:
            await self._ensure_user_membership(
                user_id=user_id,
                company_id=company_id,
            )
        company = await Company.get_active_by_id(self.db, company_id)
        if not company:
            raise CompanyNotFoundException(company_id=company_id)

        update_data = data.model_dump(exclude_unset=True)
        iban = update_data.get("iban_try")
        if iban:
            update_data["iban_try"] = normalize_iban(iban)
        company.update_from_dict(update_data)

        await self.db.commit()
        await self.db.refresh(company)

        logger.info(
            "Company updated",
            extra={
                "company_id": str(company.id),
                "company_name": company.name,
            },
        )
        return company

    async def deactivate_company(
        self, company_id: uuid.UUID, user_id: uuid.UUID | None = None
    ) -> Company:
        """Deactivate a company. Only active companies can be deactivated.

        Args:
            company_id: Company ID
            user_id: Optional user ID for membership verification

        Returns:
            Deactivated company

        Raises:
            CompanyNotFoundException: If company not found or not active
        """
        if user_id is not None:
            await self._ensure_user_membership(
                user_id=user_id,
                company_id=company_id,
            )
        company = await Company.get_active_by_id(self.db, company_id)

        if not company:
            raise CompanyNotFoundException(company_id=company_id)

        company.deactivate()

        await self.db.commit()
        await self.db.refresh(company)

        logger.info(
            "Company deactivated",
            extra={"company_id": str(company.id), "company_name": company.name},
        )
        return company

    async def activate_company(
        self, company_id: uuid.UUID, user_id: uuid.UUID | None = None
    ) -> Company:
        """Activate a company. Only inactive companies can be activated.

        Args:
            company_id: Company ID
            user_id: Optional user ID for membership verification

        Returns:
            Activated company

        Raises:
            CompanyNotFoundException: If company not found
        """
        if user_id is not None:
            await self._ensure_user_membership(
                user_id=user_id,
                company_id=company_id,
            )
        company = await Company.get_by_id(self.db, company_id)

        if not company or company.is_active:
            raise CompanyNotFoundException(company_id=company_id)

        company.activate()

        await self.db.commit()
        await self.db.refresh(company)

        logger.info(
            "Company activated",
            extra={"company_id": str(company.id), "company_name": company.name},
        )
        return company

    async def list_my_companies(
        self,
        user: User,
        page: int,
        limit: int,
        search: str | None,
    ) -> tuple[list[MyCompanyListItem], int]:
        """List companies where the user is an active member.
Companies may be active or inactive.

        Args:
            user: Authenticated user
            page: Page number (1-based)
            limit: Page size
            search: Optional search term for company name

        Returns:
            Tuple of (items, total_count)
        """
        page, limit = normalize_pagination(page, limit)
        search = normalize_search(search)

        rows, total = await UserCompany.list_active_companies_for_user_with_role(
            self.db,
            user_id=user.id,
            search=search,
            page=page,
            limit=limit,
        )

        items = [
            MyCompanyListItem(
                id=company.id,
                name=company.name,
                is_active=company.is_active,
                role=role_name,
            )
            for company, role_name in rows
        ]
        return items, total

    async def list_company_members(
        self, company_id: uuid.UUID, user_id: uuid.UUID | None = None
    ) -> list[CompanyMemberListItem]:
        """List members of a company including both active and inactive memberships.

        Args:
            company_id: Company ID
            user_id: Optional user ID for membership verification

        Returns:
            List of company members
        """
        if user_id is not None:
            await self._ensure_user_membership(
                user_id=user_id,
                company_id=company_id,
            )
        company = await Company.get_by_id(self.db, company_id)
        if not company:
            raise CompanyNotFoundException(company_id=company_id)

        rows = await UserCompany.list_members_for_company(
            self.db,
            company_id=company_id,
        )

        return [
            CompanyMemberListItem(
                user_id=user.id,
                email=user.email,
                full_name=user.full_name,
                role=role_name,
                is_active=membership_is_active,
                joined_at=joined_at,
            )
            for user, role_name, membership_is_active, joined_at in rows
        ]

    async def create_company_sector(
        self,
        company_id: uuid.UUID,
        data: CompanySectorCreateRequest,
        user_id: uuid.UUID | None = None,
    ) -> CompanySector:
        """Create a new company sector.

        Args:
            company_id: Company ID
            data: Sector creation data
            user_id: Optional user ID for membership verification

        Returns:
            Created company sector

        Raises:
            CompanyNotFoundException: If company not found or not active
            CompanySectorConflictException: If sector with same NACE code already exists
        """
        if user_id is not None:
            await self._ensure_user_membership(
                user_id=user_id,
                company_id=company_id,
            )
        company = await Company.get_active_by_id(self.db, company_id)
        if not company:
            raise CompanyNotFoundException(company_id=company_id)

        if await CompanySector.exists_for_company(
            self.db,
            company_id=company_id,
            nace_code=data.nace_code,
        ):
            raise CompanySectorConflictException(nace_code=data.nace_code)

        sector = await CompanySector.create(
            self.db,
            company_id=company_id,
            nace_code=data.nace_code,
            nace_name=data.nace_name,
            brand_name=data.brand_name,
        )

        await self.db.commit()
        await self.db.refresh(sector)

        logger.info(
            "Company sector created",
            extra={
                "sector_nace_code": sector.nace_code,
                "company_id": str(company_id),
                "company_name": company.name,
            },
        )
        return sector

    async def list_company_sectors(
        self, company_id: uuid.UUID
    ) -> list[CompanySector]:
        """List sectors for a company.

        Args:
            company_id: Company ID

        Returns:
            List of company sectors ordered by created_at asc

        Raises:
            CompanyNotFoundException: If company not found
        """
        company = await Company.get_by_id(self.db, company_id)
        if not company:
            raise CompanyNotFoundException(company_id=company_id)

        return await CompanySector.list_for_company(
            self.db,
            company_id=company_id,
        )

    async def delete_company_sector(
        self,
        company_id: uuid.UUID,
        sector_id: uuid.UUID,
        user_id: uuid.UUID | None = None,
    ) -> None:
        """Delete a company sector.

        Args:
            company_id: Company ID
            sector_id: Sector ID
            user_id: Optional user ID for membership verification

        Raises:
            CompanyNotFoundException: If company not found or not active
            CompanySectorNotFoundException: If sector not found or not belonging to company
        """
        if user_id is not None:
            await self._ensure_user_membership(
                user_id=user_id,
                company_id=company_id,
            )
        company = await Company.get_active_by_id(self.db, company_id)
        if not company:
            raise CompanyNotFoundException(company_id=company_id)

        deleted_id = await CompanySector.delete_for_company(
            self.db,
            sector_id=sector_id,
            company_id=company_id,
        )

        if deleted_id is None:
            raise CompanySectorNotFoundException(sector_id=sector_id)

        await self.db.commit()

        logger.info(
            "Company sector deleted",
            extra={
                "sector_id": str(sector_id),
                "company_id": str(company_id),
            },
        )

    async def update_company_sector_brand(
        self,
        company_id: uuid.UUID,
        sector_id: uuid.UUID,
        brand_name: str | None,
        user_id: uuid.UUID | None = None,
    ) -> CompanySector:
        """Update a company sector's brand name.

        Args:
            company_id: Company ID
            sector_id: Sector ID
            brand_name: New brand name
            user_id: Optional user ID for membership verification

        Returns:
            Updated sector

        Raises:
            CompanyNotFoundException: If company not found or not active
            CompanySectorNotFoundException: If sector not found or not belonging to company
        """
        if user_id is not None:
            await self._ensure_user_membership(
                user_id=user_id,
                company_id=company_id,
            )
        company = await Company.get_active_by_id(self.db, company_id)
        if not company:
            raise CompanyNotFoundException(company_id=company_id)

        sector = await CompanySector.get_for_company(
            self.db, sector_id, company_id
        )
        if not sector:
            raise CompanySectorNotFoundException(sector_id=sector_id)

        sector.update_brand_name(brand_name)

        await self.db.commit()
        await self.db.refresh(sector)

        logger.info(
            "Company sector brand updated",
            extra={
                "sector_id": str(sector_id),
                "company_id": str(company_id),
                "company_name": company.name,
            },
        )
        return sector
