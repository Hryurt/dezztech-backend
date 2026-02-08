import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import InvalidCredentialsException
from src.auth.schemas import LoginRequest, RegisterRequest
from src.auth.utils import create_access_token
from src.logger import get_logger
from src.users.exceptions import UserInactiveException, UserNotFoundException
from src.users.models import User
from src.users.schemas import UserCreateInternal

logger = get_logger(__name__)


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncSession):
        """Initialize AuthService with database session.

        Args:
            db: Database session
        """
        self.db = db

    async def register(self, data: RegisterRequest) -> str:
        """Register a new user.

        Args:
            data: Registration data (email, password, full_name)

        Returns:
            JWT access token

        Raises:
            UserAlreadyExistsException: If user with email already exists
        """
        # Create user data with default flags
        user_data = UserCreateInternal(
            email=data.email,
            password=data.password,
            full_name=data.full_name,
            is_active=True,
            is_superuser=False,
        )

        # Create user (password will be hashed in User.create)
        user = await User.create(db=self.db, data=user_data)

        logger.info(f"New user registered: {user.email} (ID: {user.id})")

        # Generate access token
        access_token = create_access_token(subject=user.id)

        return access_token

    async def login(self, data: LoginRequest) -> str:
        """Authenticate user and return access token.

        Args:
            data: Login credentials (email, password)

        Returns:
            JWT access token

        Raises:
            InvalidCredentialsException: If credentials are invalid
            UserInactiveException: If user is inactive
        """
        # Get user by email
        user = await User.get_by_email(self.db, data.email)

        # Check if user exists and password is correct
        if not user or not user.check_password(data.password):
            logger.warning(f"Failed login attempt for email: {data.email}")
            raise InvalidCredentialsException()

        # Check if user is active
        if not user.is_active:
            logger.warning(f"Inactive user login attempt: {user.email} (ID: {user.id})")
            raise UserInactiveException(user_id=user.id)

        logger.info(f"User logged in: {user.email} (ID: {user.id})")

        # Generate access token
        access_token = create_access_token(subject=user.id)

        return access_token

    async def get_user_by_id(self, user_id: uuid.UUID) -> User:
        """Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User object

        Raises:
            UserNotFoundException: If user not found
        """
        user = await User.get_by_id(self.db, user_id)

        if not user:
            logger.warning(f"User not found: {user_id}")
            raise UserNotFoundException(user_id=user_id)

        return user
