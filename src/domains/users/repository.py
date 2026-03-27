import uuid
from typing import TYPE_CHECKING

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.users.models import User

if TYPE_CHECKING:
    from src.domains.users.schemas import UserCreateInternal


class UserRepository:
    """Repository for User database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """Get a user by ID."""
        return await self.db.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        """Get a user by email."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def exists(self, email: str) -> bool:
        """Check if user with email exists."""
        user = await self.get_by_email(email)
        return user is not None

    async def email_or_pending_exists(self, email: str) -> bool:
        """Check if email exists in either email or pending_email column."""
        result = await self.db.execute(
            select(User).where(or_(User.email == email, User.pending_email == email))
        )
        return result.scalar_one_or_none() is not None

    async def get_active_users(self) -> list[User]:
        """Get all active users."""
        result = await self.db.execute(select(User).where(User.is_active))
        return list(result.scalars().all())

    async def create(self, data: "UserCreateInternal") -> User:
        """Create a new user.

        Args:
            data: User creation data

        Returns:
            Created user object (added to session, not committed)
        """
        user = User(
            email=data.email,
            first_name=data.first_name,
            last_name=data.last_name,
            is_active=data.is_active,
            phone_number=data.phone_number,
            how_did_you_hear=data.how_did_you_hear,
        )
        user.set_password(data.password)
        self.db.add(user)
        return user

    async def create_oauth_user(
        self,
        *,
        email: str,
        first_name: str,
        last_name: str,
    ) -> User:
        """Create a new user from OAuth (no password).

        Returns:
            Created user object (added to session, not committed)
        """
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
            password_hash=None,
        )
        self.db.add(user)
        return user
