import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, Enum, String, Uuid, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.auth.utils import hash_password, validate_password_strength, verify_password
from src.database import Base
from src.models import TimestampMixin

if TYPE_CHECKING:
    from src.users.schemas import UserCreateInternal


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class User(Base, TimestampMixin):
    """User model for authentication and user management."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            name="user_role",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        nullable=False,
        default=UserRole.USER,
    )
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    how_did_you_hear: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    pending_email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        unique=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    password_reset_tokens = relationship(
        "PasswordResetToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )

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
        return verify_password(password, self.password_hash)

    def set_password(self, password: str) -> None:
        """Hash and set user password.

        Args:
            password: Plain text password to hash
        """
        validate_password_strength(password)
        self.password_hash = hash_password(password)

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
    async def email_or_pending_exists(cls, db: AsyncSession, email: str) -> bool:
        """Check if email exists in either email or pending_email column.

        Args:
            db: Database session
            email: Email to check

        Returns:
            True if any user has this email or pending_email
        """
        result = await db.execute(
            select(cls).where(or_(cls.email == email, cls.pending_email == email))
        )
        return result.scalar_one_or_none() is not None

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
    async def create(cls, db: AsyncSession, data: "UserCreateInternal") -> "User":
        """Create a new user.

        Args:
            db: Database session
            data: User creation data

        Returns:
            Created user object
        """
        user = cls(
            email=data.email,
            first_name=data.first_name,
            last_name=data.last_name,
            is_active=data.is_active,
            phone_number=data.phone_number,
            how_did_you_hear=data.how_did_you_hear,
        )
        user.set_password(data.password)
        db.add(user)
        return user
