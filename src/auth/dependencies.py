import uuid

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
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
from src.users.models import User, UserRole

logger = get_logger(__name__)

# HTTPBearer security scheme for OpenAPI / Swagger UI
http_bearer = HTTPBearer(auto_error=False)


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """Get AuthService instance with database session.

    Args:
        db: Database session from dependency

    Returns:
        AuthService instance
    """
    return AuthService(db)


async def get_token_from_header(
    credentials: HTTPAuthorizationCredentials | None = Depends(http_bearer),
) -> str:
    """Extract JWT token from Authorization header.

    Args:
        credentials: HTTP Bearer credentials from Authorization header

    Returns:
        JWT token string

    Raises:
        TokenMissingException: If authorization header is missing
    """
    if credentials is None:
        raise TokenMissingException()

    return credentials.credentials


async def get_current_user(
    token: str = Depends(get_token_from_header),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """Get current authenticated active user from JWT token.

    Args:
        token: JWT token from Authorization header
        auth_service: AuthService instance

    Returns:
        Current active user object

    Raises:
        InvalidTokenException: If token is invalid or expired
        UserNotFoundException: If user not found
        UserInactiveException: If user is inactive (deactivated)
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

    # Get user from database
    user = await auth_service.get_user_by_id(user_id)

    if not user.is_active:
        logger.warning(
            f"Inactive user attempted access (ID: {user.id})"
        )
        raise UserInactiveException(user_id=user.id)

    return user


# Alias for backward compatibility with routers; get_current_user enforces is_active
get_current_active_user = get_current_user


async def require_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Require current user to have SUPER_ADMIN role.

    Args:
        current_user: Current user from get_current_user

    Returns:
        Current user if SUPER_ADMIN

    Raises:
        InsufficientPermissionsException: If user role is not SUPER_ADMIN
    """
    if current_user.role != UserRole.SUPER_ADMIN:
        logger.warning(
            f"Non-super-admin attempted super-admin action: {current_user.email} (ID: {current_user.id})"
        )
        raise InsufficientPermissionsException(required_permission="super_admin")

    return current_user


def require_role(required_role: UserRole):
    """Create a dependency that requires the current user to have the specified role.

    Args:
        required_role: The UserRole the user must have

    Returns:
        Dependency that returns current user if role matches

    Example:
        @router.get("/admin-only", dependencies=[Depends(require_role(UserRole.ADMIN))])
    """

    async def _require_role(
        current_user: User = Depends(get_current_user),
    ) -> User:
        """Require current user to have the specified role.

        Args:
            current_user: Current user from get_current_user

        Returns:
            Current user if role matches

        Raises:
            InsufficientPermissionsException: If user role does not match
        """
        if current_user.role != required_role:
            logger.warning(
                f"User lacks required role: {current_user.email} (ID: {current_user.id}), required: {required_role.value}"
            )
            raise InsufficientPermissionsException(required_permission=required_role.value)

        return current_user

    return _require_role
