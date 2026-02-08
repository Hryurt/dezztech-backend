import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Base User schema (shared fields)
class UserBase(BaseModel):
    """Base User schema with common fields."""

    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)


# Schema for creating a user
class UserCreate(UserBase):
    """Schema for user registration/creation."""

    password: str = Field(min_length=8, max_length=100)


# Schema for internal user creation (with additional fields)
class UserCreateInternal(UserCreate):
    """Schema for internal user creation with system flags."""

    is_active: bool = True
    is_superuser: bool = False


# Schema for updating a user
class UserUpdate(BaseModel):
    """Schema for updating user information."""

    email: EmailStr | None = None
    full_name: str | None = Field(None, min_length=1, max_length=255)
    password: str | None = Field(None, min_length=8, max_length=100)
    is_active: bool | None = None


# Schema for user response (API output)
class UserResponse(UserBase):
    """Schema for user API response."""

    id: uuid.UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Schema for user in database (internal use)
class UserInDB(UserResponse):
    """Schema for user with hashed password (internal use only)."""

    hashed_password: str


# Schema for listing users with pagination
class UserListResponse(BaseModel):
    """Schema for paginated user list response."""

    users: list[UserResponse]
    total: int
    page: int
    page_size: int
