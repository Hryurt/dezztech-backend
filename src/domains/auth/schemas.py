import uuid

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from src.core.security.password_policy import validate_password_strength


# Schema for register start (optional step 1)
class RegisterStartRequest(BaseModel):
    """Schema for register start - validate email."""

    email: EmailStr


class RegisterStartResponse(BaseModel):
    """Schema for register start response."""

    ok: bool = True
    already_registered: bool


def _validate_password(v: str) -> str:
    """Validate password meets policy. Raises ValueError if invalid."""
    validate_password_strength(v)
    return v


# Schema for user registration request
class RegisterRequest(BaseModel):
    """Schema for user registration request."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=64)
    first_name: str = Field(min_length=1, max_length=100)

    _validate_password = field_validator("password")(_validate_password)
    last_name: str = Field(min_length=1, max_length=100)
    phone_number: str | None = Field(None, max_length=20)
    how_did_you_hear: str | None = Field(None, max_length=255)


# Schema for register response (returns user_id and otp_sent, NOT token)
class RegisterResponse(BaseModel):
    """Schema for register response - OTP sent."""

    user_id: uuid.UUID
    otp_sent: bool = True


# Schema for verify email request
class VerifyEmailRequest(BaseModel):
    """Schema for verify email request."""

    email: EmailStr
    code: str = Field(min_length=4, max_length=4)


class VerifyEmailResponse(BaseModel):
    """Schema for verify email response."""

    email_verified: bool = True


# Schema for resend OTP request
class ResendOtpRequest(BaseModel):
    """Schema for resend OTP request."""

    email: EmailStr


class ResendOtpResponse(BaseModel):
    """Schema for resend OTP response."""

    otp_sent: bool = True
    cooldown_seconds_remaining: int | None = None


# Schema for login request
class LoginRequest(BaseModel):
    """Schema for user login request."""

    email: EmailStr
    password: str = Field(min_length=1)
    remember_me: bool = False


# Schema for token response
class TokenResponse(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    token_type: str = "bearer"


# Schema for token payload (internal use)
class TokenPayload(BaseModel):
    """Schema for decoded JWT token payload."""

    sub: str  # Subject (user_id)
    type: str  # Token type
    exp: int  # Expiration timestamp
    iat: int  # Issued at timestamp


# Schema for forgot password request
class ForgotPasswordRequest(BaseModel):
    """Schema for forgot password request."""

    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    """Schema for forgot password response."""

    ok: bool = True


# Schema for reset password request
class ResetPasswordRequest(BaseModel):
    """Schema for reset password request."""

    token: str = Field(min_length=10, max_length=255)
    password: str = Field(min_length=8, max_length=64)
    confirm_password: str = Field(min_length=8, max_length=64)

    _validate_password = field_validator("password")(_validate_password)

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class ResetPasswordResponse(BaseModel):
    """Schema for reset password response."""

    password_reset: bool = True
