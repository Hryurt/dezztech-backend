import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from src.core.security.password_policy import validate_password_strength

from src.users.models import UserRole


# Base User schema (shared fields)
class UserBase(BaseModel):
    """Base User schema with common fields."""

    email: EmailStr
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)


def _validate_password(v: str) -> str:
    """Validate password meets policy. Raises ValueError if invalid."""
    validate_password_strength(v)
    return v


# Schema for creating a user
class UserCreate(BaseModel):
    """Schema for user registration/creation."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=64)

    _validate_password = field_validator("password")(_validate_password)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    phone_number: str | None = Field(None, max_length=20)
    how_did_you_hear: str | None = Field(None, max_length=255)


# Schema for internal user creation (with additional fields)
class UserCreateInternal(UserCreate):
    """Schema for internal user creation with system flags."""

    role: UserRole = UserRole.USER
    is_active: bool = True


def _validate_password_optional(v: str | None) -> str | None:
    """Validate password if provided. Returns None for None, else validates and returns."""
    if v is None:
        return None
    return _validate_password(v)


# Schema for updating a user
class UserUpdate(BaseModel):
    """Schema for updating user information."""

    email: EmailStr | None = None
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    password: str | None = Field(None, min_length=8, max_length=64)
    is_active: bool | None = None
    phone_number: str | None = Field(None, max_length=20)
    how_did_you_hear: str | None = Field(None, max_length=255)

    _validate_password = field_validator("password")(_validate_password_optional)


# Schema for user response (API output)
class UserResponse(BaseModel):
    """Schema for user API response."""

    id: uuid.UUID
    email: str
    first_name: str
    last_name: str
    role: UserRole
    is_active: bool
    email_verified_at: datetime | None
    phone_number: str | None
    how_did_you_hear: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Schema for user in database (internal use)
class UserInDB(UserResponse):
    """Schema for user with hashed password (internal use only)."""

    password_hash: str


# Schema for POST /users/me/email-change-request
class EmailChangeRequest(BaseModel):
    """Schema for email change request."""

    new_email: EmailStr
    current_password: str = Field(min_length=8, max_length=64)


# Schema for POST /users/me/email-change-verify
class EmailChangeVerifyRequest(BaseModel):
    """Schema for email change verification."""

    code: str = Field(min_length=4, max_length=6)


# Schema for DELETE /users/me request
class DeleteAccountRequest(BaseModel):
    """Schema for account deactivation (soft delete)."""

    current_password: str = Field(min_length=8, max_length=64)


# Schema for PATCH /users/me/password request
class UserChangePasswordRequest(BaseModel):
    """Schema for changing current user password."""

    current_password: str = Field(min_length=8, max_length=64)
    new_password: str = Field(min_length=8, max_length=64)
    confirm_password: str = Field(min_length=8, max_length=64)

    _validate_new_password = field_validator("new_password")(_validate_password)

    @model_validator(mode="after")
    def passwords_match(self):
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


# Schema for PATCH /users/me request
class UserMeUpdateRequest(BaseModel):
    """Schema for updating current user profile."""

    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    phone_number: str | None = Field(None, max_length=20)


# Schema for current user profile (self-service)
class UserMeResponse(BaseModel):
    """Schema for GET /users/me response."""

    id: uuid.UUID
    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole
    phone_number: str | None
    how_did_you_hear: str | None
    email_verified_at: datetime | None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Schema for listing users with pagination
class UserListResponse(BaseModel):
    """Schema for paginated user list response."""

    users: list[UserResponse]
    total: int
    page: int
    page_size: int
