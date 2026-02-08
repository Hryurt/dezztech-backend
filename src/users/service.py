import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.logger import get_logger
from src.users.exceptions import UserAlreadyExistsException, UserNotFoundException
from src.users.models import User
from src.users.schemas import UserCreateInternal

logger = get_logger(__name__)


class UserService:
    """Service for user management operations."""

    def __init__(self, db: AsyncSession):
        """Initialize UserService with database session.

        Args:
            db: Database session
        """
        self.db = db

    async def get_user_by_id(self, user_id: uuid.UUID) -> User:
        """Get a user by ID.

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

    async def get_user_by_email(self, email: str) -> User | None:
        """Get a user by email.

        Args:
            email: User email

        Returns:
            User object if found, None otherwise
        """
        return await User.get_by_email(self.db, email)

    async def create_user(self, data: UserCreateInternal) -> User:
        """Create a new user.

        Args:
            data: User creation data

        Returns:
            Created user object

        Raises:
            UserAlreadyExistsException: If user with email already exists
        """
        # Check if user already exists
        if await User.exists(self.db, data.email):
            logger.warning(f"Attempt to create duplicate user: {data.email}")
            raise UserAlreadyExistsException(email=data.email)

        # Create new user
        user = await User.create(db=self.db, data=data)

        logger.info(f"User created: {data.email} (ID: {user.id}, superuser: {data.is_superuser})")

        return user

    async def activate_user(self, user_id: uuid.UUID) -> User:
        """Activate a user account.

        Args:
            user_id: User ID

        Returns:
            Updated user object

        Raises:
            UserNotFoundException: If user not found
        """
        user = await self.get_user_by_id(user_id)
        user.activate()
        await self.db.commit()
        await self.db.refresh(user)
        logger.info(f"User activated: {user.email} (ID: {user.id})")
        return user

    async def deactivate_user(self, user_id: uuid.UUID) -> User:
        """Deactivate a user account.

        Args:
            user_id: User ID

        Returns:
            Updated user object

        Raises:
            UserNotFoundException: If user not found
        """
        user = await self.get_user_by_id(user_id)
        user.deactivate()
        await self.db.commit()
        await self.db.refresh(user)
        logger.info(f"User deactivated: {user.email} (ID: {user.id})")
        return user

    async def get_active_users(self) -> list[User]:
        """Get all active users.

        Returns:
            List of active users
        """
        return await User.get_active_users(self.db)
