import uuid
from typing import Optional

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from datetime import datetime

from src.domains.companies.models import (
    Company,
    CompanyInvitation,
    CompanyRole,
    CompanySector,
    UserCompany,
)


class CompanyRepository:
    """Repository for Company-related database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Company ──

    async def create(
        self,
        *,
        name: str,
        mersis_number: str,
        tax_number: str,
        tax_office: str,
        employee_count: int,
    ) -> Company:
        """Create a new Company instance and persist it."""
        company = Company(
            name=name,
            mersis_number=mersis_number,
            tax_number=tax_number,
            tax_office=tax_office,
            employee_count=employee_count,
            is_active=True,
        )
        self.db.add(company)
        await self.db.flush()
        return company

    async def get_by_id(self, company_id: uuid.UUID) -> Optional[Company]:
        """Get a company by its ID."""
        result = await self.db.execute(select(Company).where(Company.id == company_id))
        return result.scalar_one_or_none()

    async def get_active_by_id(self, company_id: uuid.UUID) -> Optional[Company]:
        """Get an active company by its ID."""
        result = await self.db.execute(
            select(Company).where(
                Company.id == company_id,
                Company.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def delete(self, company: Company) -> None:
        """Hard delete a company (cascades to related records)."""
        await self.db.delete(company)

    async def exists_by_mersis(self, mersis_number: str) -> bool:
        """Check if a company with the given MERSIS number exists."""
        return (
            await self.db.execute(
                select(Company.id).where(Company.mersis_number == mersis_number).limit(1)
            )
        ).scalar() is not None

    # ── CompanyRole ──

    async def get_role_by_name(self, name: str) -> Optional[CompanyRole]:
        """Get role by name."""
        result = await self.db.execute(select(CompanyRole).where(CompanyRole.name == name))
        return result.scalar_one_or_none()

    async def get_role_by_id(self, role_id: uuid.UUID) -> Optional[CompanyRole]:
        """Get role by ID."""
        result = await self.db.execute(select(CompanyRole).where(CompanyRole.id == role_id))
        return result.scalar_one_or_none()

    # ── UserCompany ──

    async def membership_exists(
        self, *, user_id: uuid.UUID, company_id: uuid.UUID
    ) -> bool:
        """Check if user has any membership (active or inactive) in the company."""
        stmt = (
            select(UserCompany.id)
            .where(
                UserCompany.user_id == user_id,
                UserCompany.company_id == company_id,
            )
            .limit(1)
        )
        return (await self.db.execute(stmt)).scalar() is not None

    async def create_membership(
        self,
        *,
        user_id: uuid.UUID,
        company_id: uuid.UUID,
        role_id: uuid.UUID,
    ) -> UserCompany:
        """Create a user-company membership."""
        instance = UserCompany(
            user_id=user_id,
            company_id=company_id,
            role_id=role_id,
            is_active=True,
        )
        self.db.add(instance)
        return instance

    async def list_members_for_company(
        self,
        company_id: uuid.UUID,
    ) -> list[tuple]:
        """List members of a company with their roles."""
        from src.domains.users.models import User

        stmt = (
            select(User, CompanyRole.name, UserCompany.is_active, UserCompany.created_at)
            .select_from(UserCompany)
            .join(User, UserCompany.user_id == User.id)
            .join(CompanyRole, UserCompany.role_id == CompanyRole.id)
            .where(UserCompany.company_id == company_id)
            .order_by(UserCompany.created_at.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.all())

    async def list_active_companies_for_user_with_role(
        self,
        user_id: uuid.UUID,
        search: str | None,
        page: int,
        limit: int,
    ) -> tuple[list[tuple[Company, str]], int]:
        """List active companies for a user with their roles (paginated)."""
        base_stmt = (
            select(Company, CompanyRole.name)
            .select_from(UserCompany)
            .join(Company, UserCompany.company_id == Company.id)
            .join(CompanyRole, UserCompany.role_id == CompanyRole.id)
            .where(
                UserCompany.user_id == user_id,
                UserCompany.is_active.is_(True),
            )
        )

        if search:
            base_stmt = base_stmt.where(Company.name.ilike(f"%{search}%"))

        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0

        offset = (page - 1) * limit

        stmt = (
            base_stmt
            .order_by(Company.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return list(result.all()), total

    # ── CompanySector ──

    async def create_sector(
        self,
        *,
        company_id: uuid.UUID,
        nace_code: str,
        nace_name: str,
    ) -> CompanySector:
        """Create a new company sector (NACE code)."""
        sector = CompanySector(
            company_id=company_id,
            nace_code=nace_code,
            nace_name=nace_name,
        )
        self.db.add(sector)
        return sector

    async def sector_exists_for_company(
        self,
        company_id: uuid.UUID,
        nace_code: str,
    ) -> bool:
        """Check if a sector with nace_code exists for a company."""
        stmt = (
            select(CompanySector.id)
            .where(
                CompanySector.company_id == company_id,
                CompanySector.nace_code == nace_code,
            )
            .limit(1)
        )
        return (await self.db.execute(stmt)).scalar() is not None

    async def list_sectors_for_company(
        self, company_id: uuid.UUID
    ) -> list[CompanySector]:
        """List sectors for a company ordered by created_at asc."""
        stmt = (
            select(CompanySector)
            .where(CompanySector.company_id == company_id)
            .order_by(CompanySector.created_at.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def delete_sector_for_company(
        self,
        *,
        sector_id: uuid.UUID,
        company_id: uuid.UUID,
    ) -> uuid.UUID | None:
        """Delete a sector belonging to a company and return the deleted id."""
        stmt = (
            delete(CompanySector)
            .where(
                CompanySector.id == sector_id,
                CompanySector.company_id == company_id,
            )
            .returning(CompanySector.id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # ── CompanyInvitation ──

    async def create_invitation(
        self,
        *,
        company_id: uuid.UUID,
        email: str,
        role_id: uuid.UUID,
        invited_by: uuid.UUID,
        token: str,
        expires_at: datetime,
    ) -> CompanyInvitation:
        """Create a company invitation."""
        invitation = CompanyInvitation(
            company_id=company_id,
            email=email,
            role_id=role_id,
            invited_by=invited_by,
            token=token,
            expires_at=expires_at,
        )
        self.db.add(invitation)
        return invitation

    async def get_pending_invitation(
        self,
        company_id: uuid.UUID,
        email: str,
    ) -> Optional[CompanyInvitation]:
        """Get a pending (not accepted, not expired) invitation."""
        now = datetime.now()
        result = await self.db.execute(
            select(CompanyInvitation).where(
                CompanyInvitation.company_id == company_id,
                CompanyInvitation.email == email,
                CompanyInvitation.is_accepted.is_(False),
                CompanyInvitation.expires_at > now,
            )
        )
        return result.scalar_one_or_none()

    async def get_invitation_by_token(
        self, token: str
    ) -> Optional[CompanyInvitation]:
        """Get an invitation by its token."""
        result = await self.db.execute(
            select(CompanyInvitation).where(CompanyInvitation.token == token)
        )
        return result.scalar_one_or_none()
