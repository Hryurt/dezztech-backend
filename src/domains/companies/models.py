import uuid
from datetime import date
from typing import Optional

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Integer,
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

    def update_brand_name(self, brand_name: str | None) -> None:
        """Update the brand name."""
        self.brand_name = brand_name


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
