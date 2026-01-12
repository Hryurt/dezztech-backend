from pydantic import BaseModel, EmailStr, Field


# Schema for user registration request
class RegisterRequest(BaseModel):
    """Schema for user registration request."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    full_name: str = Field(min_length=1, max_length=255)


# Schema for login request
class LoginRequest(BaseModel):
    """Schema for user login request."""

    email: EmailStr
    password: str = Field(min_length=1)


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
