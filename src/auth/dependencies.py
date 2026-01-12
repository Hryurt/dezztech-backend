import uuid

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import (
    InsufficientPermissionsException,
    InvalidTokenException,
    TokenMissingException,
)
from src.auth.service import get_user_from_token
from src.auth.utils import verify_access_token
from src.database import get_db
from src.users.models import User


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
        token = authorization[7:]  # len("Bearer ") = 7
    else:
        token = authorization

    return token


async def get_current_user(
    token: str = Depends(get_token_from_header),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current authenticated user from JWT token.

    Args:
        token: JWT token from Authorization header
        db: Database session

    Returns:
        Current user object

    Raises:
        InvalidTokenException: If token is invalid or expired
        UserNotFoundException: If user not found
        UserInactiveException: If user is inactive
    """
    # Verify token and get user_id
    user_id_str = verify_access_token(token)

    if not user_id_str:
        raise InvalidTokenException()

    # Convert to UUID
    try:
        user_id = uuid.UUID(user_id_str)
    except (ValueError, AttributeError):
        raise InvalidTokenException() from None

    # Get user from database
    user = await get_user_from_token(db, user_id)

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user (additional check for active status).

    Args:
        current_user: Current user from get_current_user

    Returns:
        Current active user object

    Note:
        This is redundant as get_current_user already checks is_active,
        but kept for explicit active user requirement in routes.
    """
    # Already checked in get_user_from_token, but explicit is better
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
        raise InsufficientPermissionsException(required_permission="superuser")

    return current_user
