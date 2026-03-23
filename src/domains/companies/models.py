import uuid
from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.core.models import TimestampMixin


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


class Company(Base, TimestampMixin):
    """Company entity for managing company information.

    Fields based on PRD 8.2 (EK-YBF common fields).
    Sector-specific fields are stored in CompanySectorProfile.
    """

    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    # ── Identity (PRD 8.2) ──
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    mersis_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    tax_number: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    tax_office: Mapped[str] = mapped_column(String(100), nullable=False)
    foundation_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    employee_count: Mapped[int] = mapped_column(Integer, nullable=False)
    headquarters_address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # ── Financial (PRD 8.2) ──
    iban_try: Mapped[Optional[str]] = mapped_column(String(34), nullable=True)
    sgk_debt: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    tax_debt: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    service_export_last_year_usd: Mapped[Optional[int]] = mapped_column(
        Numeric(precision=15, scale=2), nullable=True
    )
    foreign_income_last_year_usd: Mapped[Optional[int]] = mapped_column(
        Numeric(precision=15, scale=2), nullable=True
    )

    # ── Activity (PRD 8.2) ──
    nace_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    activity_sectors: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)
    exporter_unions: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)
    hib_member_no: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # ── Contact (PRD 8.2) ──
    contact_full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    kep_address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # ── Relationships ──
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
    brands: Mapped[list["CompanyBrand"]] = relationship(
        "CompanyBrand",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    sector_profile: Mapped["CompanySectorProfile"] = relationship(
        "CompanySectorProfile",
        back_populates="company",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )

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
            "sgk_debt",
            "tax_debt",
            "service_export_last_year_usd",
            "foreign_income_last_year_usd",
            "nace_code",
            "activity_sectors",
            "exporter_unions",
            "hib_member_no",
            "contact_full_name",
            "contact_phone",
            "contact_email",
            "email",
            "phone",
            "website",
            "kep_address",
        }
        for field, value in data.items():
            if field in allowed_fields and hasattr(self, field):
                setattr(self, field, value)


class CompanyInvitation(Base, TimestampMixin):
    """Invitation to join a company with a specific role.

    Token is sent via email. Expires after 7 days.
    If invitee is not registered, they can sign up using the token.
    """

    __tablename__ = "company_invitations"

    INVITATION_VALIDITY_DAYS = 7

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("company_roles.id", ondelete="RESTRICT"),
        nullable=False,
    )
    invited_by: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    token: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_accepted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    company: Mapped["Company"] = relationship("Company", lazy="selectin")
    role: Mapped["CompanyRole"] = relationship("CompanyRole", lazy="selectin")

    def is_expired(self) -> bool:
        """Check if invitation has expired."""
        return datetime.now(timezone.utc) > self.expires_at

    def accept(self) -> None:
        """Mark invitation as accepted."""
        self.is_accepted = True


class CompanySector(Base, TimestampMixin):
    """Company NACE sector sub-entity (many per Company)."""

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

    def update_brand_name(self, brand_name: str | None) -> None:
        """Update the brand name."""
        self.brand_name = brand_name


class CompanyBrand(Base, TimestampMixin):
    """Brand for a company (PRD 8.2 — repeatable).

    A company can have multiple brands. Each brand has a name and optional URL.
    """

    __tablename__ = "company_brands"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "brand_name",
            name="uq_company_brand_name",
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
    brand_name: Mapped[str] = mapped_column(String(255), nullable=False)
    brand_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="brands",
        lazy="selectin",
    )


class CompanySectorProfile(Base, TimestampMixin):
    """Sector-specific company profile data (PRD 8.3).

    One profile per company. Stores the company's sector type and all
    sector-specific fields as a JSON document.

    The sector_type determines which fields are expected in the data column.
    Form builder references individual fields via sector_type + key path.
    """

    __tablename__ = "company_sector_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    sector_type: Mapped[str] = mapped_column(String(50), nullable=False)
    data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="sector_profile",
        lazy="selectin",
    )


class UserCompany(Base, TimestampMixin):
    """User-company association (many-to-many with role)."""

    __tablename__ = "users_companies"
    __table_args__ = (
        UniqueConstraint("user_id", "company_id", name="uq_users_companies_user_company"),
    )

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
