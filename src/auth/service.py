import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import InvalidCredentialsException
from src.auth.schemas import LoginRequest, RegisterRequest
from src.auth.utils import create_access_token, hash_password, verify_password
from src.users.exceptions import UserInactiveException
from src.users.models import User
from src.users.service import create_user, get_user_by_email


async def register(db: AsyncSession, data: RegisterRequest) -> str:
    """Register a new user.

    Args:
        db: Database session
        data: Registration data (email, password, full_name)

    Returns:
        JWT access token

    Raises:
        UserAlreadyExistsException: If user with email already exists
    """
    # Hash password
    hashed_password = hash_password(data.password)

    # Create user with default values
    user = await create_user(
        db=db,
        email=data.email,
        hashed_password=hashed_password,
        full_name=data.full_name,
        is_active=True,  # Default active
        is_superuser=False,  # Default not superuser
    )

    # Generate access token
    access_token = create_access_token(subject=user.id)

    return access_token


async def login(db: AsyncSession, data: LoginRequest) -> str:
    """Authenticate user and return access token.

    Args:
        db: Database session
        data: Login credentials (email, password)

    Returns:
        JWT access token

    Raises:
        InvalidCredentialsException: If credentials are invalid
        UserInactiveException: If user is inactive
    """
    # Get user by email
    user = await get_user_by_email(db, data.email)

    # Check if user exists and password is correct
    if not user or not verify_password(data.password, user.hashed_password):
        raise InvalidCredentialsException()

    # Check if user is active
    if not user.is_active:
        raise UserInactiveException(user_id=user.id)

    # Generate access token
    access_token = create_access_token(subject=user.id)

    return access_token


async def get_user_from_token(db: AsyncSession, user_id: uuid.UUID) -> User:
    """Get user from database by user_id (from token).

    Args:
        db: Database session
        user_id: User ID from token

    Returns:
        User object

    Raises:
        UserNotFoundException: If user not found
        UserInactiveException: If user is inactive
    """
    from src.users.service import get_user_by_id

    user = await get_user_by_id(db, user_id)

    # Check if user is active
    if not user.is_active:
        raise UserInactiveException(user_id=user.id)

    return user
