import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, String, Uuid, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from src.auth.utils import hash_password, verify_password
from src.database import Base
from src.models import TimestampMixin

if TYPE_CHECKING:
    from src.users.schemas import UserCreateData


class User(Base, TimestampMixin):
    """User model for authentication and user management."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"

    # ──────────────────────────────────────────────
    # Domain Methods (Instance Methods)
    # ──────────────────────────────────────────────

    def activate(self) -> None:
        """Activate user account."""
        self.is_active = True

    def deactivate(self) -> None:
        """Deactivate user account."""
        self.is_active = False

    def check_password(self, password: str) -> bool:
        """Verify password against stored hash.

        Args:
            password: Plain text password to verify

        Returns:
            True if password matches, False otherwise
        """
        return verify_password(password, self.hashed_password)

    def set_password(self, password: str) -> None:
        """Hash and set user password.

        Args:
            password: Plain text password to hash
        """
        self.hashed_password = hash_password(password)

    def is_locked(self) -> bool:
        """Check if account is locked.

        Returns:
            False (future feature - will implement login attempts tracking)
        """
        # Future feature: implement login attempts tracking
        return False

    # ──────────────────────────────────────────────
    # Query Methods (Class Methods)
    # ──────────────────────────────────────────────

    @classmethod
    async def get_by_id(cls, db: AsyncSession, user_id: uuid.UUID) -> Optional["User"]:
        """Get a user by ID.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            User object if found, None otherwise
        """
        return await db.get(cls, user_id)

    @classmethod
    async def get_by_email(cls, db: AsyncSession, email: str) -> Optional["User"]:
        """Get a user by email.

        Args:
            db: Database session
            email: User email

        Returns:
            User object if found, None otherwise
        """
        result = await db.execute(select(cls).where(cls.email == email))
        return result.scalar_one_or_none()

    @classmethod
    async def get_active_users(cls, db: AsyncSession) -> list["User"]:
        """Get all active users.

        Args:
            db: Database session

        Returns:
            List of active users
        """
        result = await db.execute(select(cls).where(cls.is_active))
        return list(result.scalars().all())

    @classmethod
    async def exists(cls, db: AsyncSession, email: str) -> bool:
        """Check if user with email exists.

        Args:
            db: Database session
            email: Email to check

        Returns:
            True if user exists, False otherwise
        """
        user = await cls.get_by_email(db, email)
        return user is not None

    @classmethod
    async def create(cls, db: AsyncSession, data: "UserCreateData") -> "User":
        """Create a new user.

        Args:
            db: Database session
            data: User creation data

        Returns:
            Created user object
        """
        user = cls(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            is_active=data.is_active,
            is_superuser=data.is_superuser,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
