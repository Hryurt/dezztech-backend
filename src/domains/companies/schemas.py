import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CompanyCreateRequest(BaseModel):
    """Request schema for creating a company."""

    name: str = Field(..., min_length=1, max_length=255)
    mersis_number: str = Field(..., min_length=8, max_length=50)
    tax_number: str = Field(..., min_length=5, max_length=20)
    tax_office: str = Field(..., min_length=2, max_length=100)
    employee_count: int = Field(..., ge=0)
    foundation_date: Optional[date] = None
    headquarters_address: Optional[str] = None
    iban_try: Optional[str] = None
    nace_code: Optional[str] = None
    activity_sector: Optional[str] = None
    exporter_union: Optional[str] = None
    hib_member_no: Optional[str] = None
    contact_full_name: Optional[str] = None
    contact_phone: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    kep_address: Optional[str] = None


class MyCompanyListItem(BaseModel):
    """Response schema for company list item (user's companies)."""

    id: uuid.UUID
    name: str
    is_active: bool
    role: str

    model_config = ConfigDict(from_attributes=True)


class PaginatedCompanyListResponse(BaseModel):
    """Response schema for paginated company list."""

    items: list[MyCompanyListItem]
    total: int
    page: int
    limit: int

    model_config = ConfigDict(from_attributes=True)


class CompanyMemberListItem(BaseModel):
    """Response schema for company member list item."""

    user_id: uuid.UUID
    email: str
    full_name: str | None
    role: str
    is_active: bool
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CompanyResponse(BaseModel):
    """Response schema for company data."""

    id: uuid.UUID
    name: str
    mersis_number: str
    tax_number: str
    tax_office: str
    employee_count: int
    foundation_date: Optional[date] = None
    headquarters_address: Optional[str] = None
    iban_try: Optional[str] = None
    nace_code: Optional[str] = None
    activity_sector: Optional[str] = None
    exporter_union: Optional[str] = None
    hib_member_no: Optional[str] = None
    contact_full_name: Optional[str] = None
    contact_phone: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    kep_address: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CompanyUpdateRequest(BaseModel):
    """Request schema for updating company (partial update)."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    tax_office: str | None = Field(default=None, min_length=2, max_length=100)
    employee_count: int | None = Field(default=None, ge=0)
    foundation_date: Optional[date] = None
    headquarters_address: Optional[str] = None
    iban_try: Optional[str] = None
    nace_code: Optional[str] = None
    activity_sector: Optional[str] = None
    exporter_union: Optional[str] = None
    hib_member_no: Optional[str] = None
    contact_full_name: Optional[str] = None
    contact_phone: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    kep_address: Optional[str] = None


class CompanySectorCreateRequest(BaseModel):
    """Request schema for creating a company sector."""

    nace_code: str = Field(..., min_length=2, max_length=20)
    nace_name: str = Field(..., min_length=2, max_length=255)
    brand_name: Optional[str] = None


class CompanySectorUpdateRequest(BaseModel):
    """Request schema for updating a company sector."""

    brand_name: Optional[str] = None


class CompanySectorResponse(BaseModel):
    """Response schema for company sector."""

    id: uuid.UUID
    company_id: uuid.UUID
    nace_code: str
    nace_name: str
    brand_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
