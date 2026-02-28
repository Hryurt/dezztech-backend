from fastapi import APIRouter, Depends, status

from src.auth.dependencies import get_auth_service, get_current_user
from src.auth.schemas import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    RegisterStartRequest,
    RegisterStartResponse,
    ResendOtpRequest,
    ResendOtpResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    TokenResponse,
    VerifyEmailRequest,
    VerifyEmailResponse,
)
from src.auth.service import AuthService
from src.users.models import User
from src.users.schemas import UserResponse

router = APIRouter()


@router.post(
    "/register/start",
    response_model=RegisterStartResponse,
    status_code=status.HTTP_200_OK,
    summary="Start registration",
    description="Validate email format (optional step 1)",
)
async def start_register(
    data: RegisterStartRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Check email existence and return registration status."""
    return await auth_service.start_register(email=data.email)


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create user and send OTP to verify email",
)
async def register_user(
    data: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Register a new user and send OTP.

    - **email**: Valid email address
    - **password**: Minimum 8 characters
    - **first_name**, **last_name**: User names

    Returns user_id and otp_sent (OTP logged server-side).
    """
    return await auth_service.register(data=data)


@router.post(
    "/register/verify-email",
    response_model=VerifyEmailResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify email with OTP",
    description="Verify email using 4-digit OTP code",
)
async def verify_email(
    data: VerifyEmailRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Verify email with OTP code."""
    await auth_service.verify_email(email=data.email, code=data.code)
    return VerifyEmailResponse(email_verified=True)


@router.post(
    "/register/resend-otp",
    response_model=ResendOtpResponse,
    status_code=status.HTTP_200_OK,
    summary="Resend OTP",
    description="Resend OTP code (60s cooldown)",
)
async def resend_otp(
    data: ResendOtpRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Resend OTP for email verification."""
    return await auth_service.resend_otp(email=data.email)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description="Authenticate user and return access token",
)
async def login_user(
    data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Login user with email and password.

    - **email**: User's email address
    - **password**: User's password

    Returns JWT access token.
    """
    return await auth_service.login(data=data)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Get currently authenticated user's information",
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get current authenticated user's information.

    Requires valid JWT token in Authorization header.
    """
    return current_user


@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse,
    status_code=status.HTTP_200_OK,
    summary="Request password reset",
    description="Send password reset link if email exists",
)
async def forgot_password(
    data: ForgotPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Request password reset for the given email."""
    await auth_service.forgot_password(email=data.email)
    return ForgotPasswordResponse(ok=True)


@router.post(
    "/reset-password",
    response_model=ResetPasswordResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset user password",
    description="Reset password using reset token",
)
async def reset_password(
    data: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Reset password using reset token."""
    await auth_service.reset_password(data.token, data.password)
    return ResetPasswordResponse(password_reset=True)
