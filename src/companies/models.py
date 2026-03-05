import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    Uuid,
    delete,
    func,
    select,
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models import TimestampMixin


class CompanyRole(Base):
    """Company role entity (owner, admin, accountant, guest, etc.)."""

    __tablename__ = "company_roles"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    permissions: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user_companies: Mapped[list["UserCompany"]] = relationship(
        "UserCompany",
        back_populates="role",
        lazy="selectin",
    )

    @classmethod
    async def get_by_name(
        cls, db: AsyncSession, name: str
    ) -> Optional["CompanyRole"]:
        """Get role by name."""
        result = await db.execute(select(cls).where(cls.name == name))
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_id(
        cls, db: AsyncSession, role_id: uuid.UUID
    ) -> Optional["CompanyRole"]:
        """Get role by ID."""
        result = await db.execute(select(cls).where(cls.id == role_id))
        return result.scalar_one_or_none()


class Company(Base, TimestampMixin):
    """Company entity for managing company information."""

    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    mersis_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    tax_number: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    tax_office: Mapped[str] = mapped_column(String(100), nullable=False)
    employee_count: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    # Company profile fields
    foundation_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    headquarters_address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    # Financial
    iban_try: Mapped[Optional[str]] = mapped_column(String(34), nullable=True)
    # Activity
    nace_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    activity_sector: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    exporter_union: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    hib_member_no: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    # Contact
    contact_full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    kep_address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # NOTE:
    # This relationship represents memberships (UserCompany),
    # not direct users. Each entry contains role information.
    users: Mapped[list["UserCompany"]] = relationship(
        "UserCompany",
        back_populates="company",
        cascade="all, delete-orphan",
    )
    sectors: Mapped[list["CompanySector"]] = relationship(
        "CompanySector",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # ──────────────────────────────────────────────
    # Factory Methods (Class Methods)
    # ──────────────────────────────────────────────

    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        *,
        name: str,
        mersis_number: str,
        tax_number: str,
        tax_office: str,
        employee_count: int,
    ) -> "Company":
        """Create a new Company instance and persist it."""
        company = cls(
            name=name,
            mersis_number=mersis_number,
            tax_number=tax_number,
            tax_office=tax_office,
            employee_count=employee_count,
            is_active=True,
        )
        db.add(company)
        await db.flush()
        return company

    # ──────────────────────────────────────────────
    # Domain Methods (Instance Methods)
    # ──────────────────────────────────────────────

    def activate(self) -> None:
        """Activate the company."""
        self.is_active = True

    def deactivate(self) -> None:
        """Deactivate the company."""
        self.is_active = False

    def update_from_dict(self, data: dict) -> None:
        """Safely update allowed company fields from a dictionary.

        Only fields explicitly listed in allowed_fields will be updated.
        This prevents accidental or malicious mass assignment.
        """
        allowed_fields = {
            "name",
            "tax_office",
            "employee_count",
            "foundation_date",
            "headquarters_address",
            "iban_try",
            "nace_code",
            "activity_sector",
            "exporter_union",
            "hib_member_no",
            "contact_full_name",
            "contact_phone",
            "email",
            "phone",
            "website",
            "kep_address",
        }
        for field, value in data.items():
            if field in allowed_fields and hasattr(self, field):
                setattr(self, field, value)

    # ──────────────────────────────────────────────
    # Query Methods (Class Methods)
    # ──────────────────────────────────────────────

    @classmethod
    async def get_by_id(
        cls, db: AsyncSession, company_id: uuid.UUID
    ) -> Optional["Company"]:
        """Get a company by its ID.

        Args:
            db: Database session
            company_id: Company ID

        Returns:
            Company if found, None otherwise
        """
        result = await db.execute(select(cls).where(cls.id == company_id))
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_mersis(
        cls, db: AsyncSession, mersis_number: str
    ) -> Optional["Company"]:
        """Get a company by its MERSIS number.

        Args:
            db: Database session
            mersis_number: MERSIS number

        Returns:
            Company if found, None otherwise
        """
        result = await db.execute(select(cls).where(cls.mersis_number == mersis_number))
        return result.scalar_one_or_none()

    @classmethod
    async def exists_by_mersis(cls, db: AsyncSession, mersis_number: str) -> bool:
        """Check if a company with the given MERSIS number exists.

        Args:
            db: Database session
            mersis_number: MERSIS number

        Returns:
            True if exists, False otherwise
        """
        return (
            await db.execute(
                select(cls.id).where(cls.mersis_number == mersis_number).limit(1)
            )
        ).scalar() is not None

    @classmethod
    async def get_active_by_id(
        cls, db: AsyncSession, company_id: uuid.UUID
    ) -> Optional["Company"]:
        """Get an active company by its ID.

        Args:
            db: Database session
            company_id: Company ID

        Returns:
            Company if found and active, None otherwise
        """
        result = await db.execute(
            select(cls).where(
                cls.id == company_id,
                cls.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()


class CompanySector(Base, TimestampMixin):
    """Company sector sub-entity (many per Company)."""

    __tablename__ = "company_sectors"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "nace_code",
            name="uq_company_sector_company_nace",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    nace_code: Mapped[str] = mapped_column(String(20), nullable=False)
    nace_name: Mapped[str] = mapped_column(String(255), nullable=False)
    brand_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="sectors",
        lazy="selectin",
    )

    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        *,
        company_id: uuid.UUID,
        nace_code: str,
        nace_name: str,
        brand_name: str | None,
    ) -> "CompanySector":
        sector = cls(
            company_id=company_id,
            nace_code=nace_code,
            nace_name=nace_name,
            brand_name=brand_name,
        )
        db.add(sector)
        return sector

    @classmethod
    async def exists_for_company(
        cls,
        db: AsyncSession,
        company_id: uuid.UUID,
        nace_code: str,
    ) -> bool:
        stmt = (
            select(cls.id)
            .where(
                cls.company_id == company_id,
                cls.nace_code == nace_code,
            )
            .limit(1)
        )
        return (await db.execute(stmt)).scalar() is not None

    @classmethod
    async def get_by_id(
        cls,
        db: AsyncSession,
        sector_id: uuid.UUID,
    ) -> Optional["CompanySector"]:
        """Get a sector by its ID."""
        result = await db.execute(select(cls).where(cls.id == sector_id))
        return result.scalar_one_or_none()

    @classmethod
    async def get_for_company(
        cls,
        db: AsyncSession,
        sector_id: uuid.UUID,
        company_id: uuid.UUID,
    ) -> Optional["CompanySector"]:
        """Get a sector by ID only if it belongs to the company."""
        result = await db.execute(
            select(cls).where(
                cls.id == sector_id,
                cls.company_id == company_id,
            )
        )
        return result.scalar_one_or_none()

    def update_brand_name(self, brand_name: str | None) -> None:
        """Update the brand name."""
        self.brand_name = brand_name

    @classmethod
    async def list_for_company(
        cls,
        db: AsyncSession,
        company_id: uuid.UUID,
    ) -> list["CompanySector"]:
        stmt = (
            select(cls)
            .where(cls.company_id == company_id)
            .order_by(cls.created_at.asc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @classmethod
    async def delete_for_company(
        cls,
        db: AsyncSession,
        *,
        sector_id: uuid.UUID,
        company_id: uuid.UUID,
    ) -> uuid.UUID | None:
        """Delete a sector belonging to a company and return the deleted id."""
        stmt = (
            delete(cls)
            .where(
                cls.id == sector_id,
                cls.company_id == company_id,
            )
            .returning(cls.id)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


class UserCompany(Base, TimestampMixin):
    """User-company association (many-to-many with role)."""

    __tablename__ = "users_companies"
    __table_args__ = (UniqueConstraint("user_id", "company_id", name="uq_users_companies_user_company"),)

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("company_roles.id", ondelete="RESTRICT"),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    user: Mapped["User"] = relationship(
        "User",
        back_populates="companies",
        lazy="selectin",
    )
    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="users",
        lazy="selectin",
    )
    role: Mapped["CompanyRole"] = relationship(
        "CompanyRole",
        back_populates="user_companies",
        lazy="selectin",
    )

    @classmethod
    async def exists_for_user_and_company(
        cls,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
        company_id: uuid.UUID,
    ) -> bool:
        """Check if user has any membership (active or inactive) in the company."""
        stmt = (
            select(cls.id)
            .where(
                cls.user_id == user_id,
                cls.company_id == company_id,
            )
            .limit(1)
        )
        return (await db.execute(stmt)).scalar() is not None

    @classmethod
    async def create_for_company(
        cls,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
        company_id: uuid.UUID,
        role_id: uuid.UUID,
    ) -> "UserCompany":
        instance = cls(
            user_id=user_id,
            company_id=company_id,
            role_id=role_id,
            is_active=True,
        )
        db.add(instance)
        return instance

    @classmethod
    async def get_active_companies_with_roles_for_user(
        cls, db: AsyncSession, user_id: uuid.UUID
    ) -> list[tuple["Company", str]]:
        """Get (Company, role_name) for user's active memberships in active companies.

        NOTE: Currently unused, may replace list_my_companies query in future refactor.
        """
        stmt = (
            select(Company, CompanyRole.name)
            .select_from(cls)
            .join(Company, cls.company_id == Company.id)
            .join(CompanyRole, cls.role_id == CompanyRole.id)
            .where(
                cls.user_id == user_id,
                cls.is_active.is_(True),
                Company.is_active.is_(True),
            )
        )
        result = await db.execute(stmt)
        return list(result.all())

    @classmethod
    async def list_members_for_company(
        cls,
        db: AsyncSession,
        company_id: uuid.UUID,
    ) -> list[tuple["User", str, bool, datetime]]:
        from src.users.models import User

        stmt = (
            select(User, CompanyRole.name, cls.is_active, cls.created_at)
            .select_from(cls)
            .join(User, cls.user_id == User.id)
            .join(CompanyRole, cls.role_id == CompanyRole.id)
            .where(cls.company_id == company_id)
            .order_by(cls.created_at.asc())
        )
        result = await db.execute(stmt)
        return list(result.all())

    @classmethod
    async def list_active_companies_for_user_with_role(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        search: str | None,
        page: int,
        limit: int,
    ) -> tuple[list[tuple["Company", str]], int]:
        base_stmt = (
            select(Company, CompanyRole.name)
            .select_from(cls)
            .join(Company, cls.company_id == Company.id)
            .join(CompanyRole, cls.role_id == CompanyRole.id)
            .where(
                cls.user_id == user_id,
                cls.is_active.is_(True),
            )
        )

        if search:
            base_stmt = base_stmt.where(Company.name.ilike(f"%{search}%"))

        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        count_result = await db.execute(count_stmt)
        total = count_result.scalar() or 0

        offset = (page - 1) * limit

        stmt = (
            base_stmt
            .order_by(Company.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        result = await db.execute(stmt)

        return list(result.all()), total
