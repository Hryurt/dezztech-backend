import uuid

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import (
    InsufficientPermissionsException,
    InvalidTokenException,
    TokenMissingException,
)
from src.auth.service import AuthService
from src.auth.utils import verify_access_token
from src.database import get_db
from src.logger import get_logger
from src.users.exceptions import UserInactiveException
from src.users.models import User

logger = get_logger(__name__)


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """Get AuthService instance with database session.

    Args:
        db: Database session from dependency

    Returns:
        AuthService instance
    """
    return AuthService(db)


async def get_token_from_header(authorization: str | None = Header(None)) -> str:
    """Extract JWT token from Authorization header.

    Args:
        authorization: Authorization header value

    Returns:
        JWT token string

    Raises:
        TokenMissingException: If authorization header is missing
    """
    if not authorization:
        raise TokenMissingException()

    # Remove "Bearer " prefix
    if authorization.startswith("Bearer "):
        token = authorization[7:]
    else:
        token = authorization

    return token


async def get_current_user(
    token: str = Depends(get_token_from_header),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """Get current authenticated user from JWT token (active or inactive).

    Args:
        token: JWT token from Authorization header
        auth_service: AuthService instance

    Returns:
        Current user object

    Raises:
        InvalidTokenException: If token is invalid or expired
        UserNotFoundException: If user not found
    """
    # Verify token and get user_id
    user_id_str = verify_access_token(token)

    if not user_id_str:
        logger.warning("Invalid token provided")
        raise InvalidTokenException()

    # Convert to UUID
    try:
        user_id = uuid.UUID(user_id_str)
    except (ValueError, AttributeError):
        logger.warning(f"Invalid UUID format in token: {user_id_str}")
        raise InvalidTokenException() from None

    # Get user from database (no active check)
    user = await auth_service.get_user_by_id(user_id)

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user from JWT token.

    Args:
        current_user: Current user from get_current_user

    Returns:
        Current active user object

    Raises:
        UserInactiveException: If user is inactive
    """
    if not current_user.is_active:
        logger.warning(
            f"Inactive user attempted to access protected resource: {current_user.email} (ID: {current_user.id})"
        )
        raise UserInactiveException(user_id=current_user.id)

    return current_user


async def require_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Require current user to be a superuser.

    Args:
        current_user: Current user from get_current_user

    Returns:
        Current user if superuser

    Raises:
        InsufficientPermissionsException: If user is not a superuser
    """
    if not current_user.is_superuser:
        logger.warning(
            f"Non-superuser attempted superuser action: {current_user.email} (ID: {current_user.id})"
        )
        raise InsufficientPermissionsException(required_permission="superuser")

    return current_user
