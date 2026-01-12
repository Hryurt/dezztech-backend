from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.auth.schemas import LoginRequest, RegisterRequest, TokenResponse
from src.auth.service import login, register
from src.database import get_db
from src.users.models import User
from src.users.schemas import UserResponse

router = APIRouter()


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account and return access token",
)
async def register_user(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user.

    - **email**: Valid email address
    - **password**: Minimum 8 characters
    - **full_name**: User's full name

    Returns JWT access token for immediate login.
    """
    access_token = await register(db=db, data=data)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description="Authenticate user and return access token",
)
async def login_user(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Login user with email and password.

    - **email**: User's email address
    - **password**: User's password

    Returns JWT access token.
    """
    access_token = await login(db=db, data=data)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )


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
