import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Uuid, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models import TimestampMixin


class PasswordResetToken(Base, TimestampMixin):
    """Password reset token for user password recovery."""

    __tablename__ = "password_reset_tokens"

    RESET_TOKEN_VALIDITY_MINUTES = 15

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship(
        "User", back_populates="password_reset_tokens", lazy="selectin"
    )

    def mark_as_used(self) -> None:
        """Mark this token as used."""
        self.is_used = True

    @classmethod
    async def create_for_user(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        token_hash: str,
        expires_at: datetime,
    ) -> "PasswordResetToken":
        """Create a new password reset token for a user.

        Args:
            db: Database session
            user_id: User ID
            token_hash: SHA256 hash of the raw token
            expires_at: Token expiration datetime

        Returns:
            Created PasswordResetToken (not committed)
        """
        token = cls(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            is_used=False,
        )
        db.add(token)
        return token

    @classmethod
    async def invalidate_active_tokens(
        cls, db: AsyncSession, user_id: uuid.UUID
    ) -> None:
        """Invalidate all active (unused) reset tokens for a user.

        Args:
            db: Database session
            user_id: User ID
        """
        result = await db.execute(
            select(cls).where(
                cls.user_id == user_id,
                cls.is_used.is_(False),
            )
        )
        for token in result.scalars().all():
            token.mark_as_used()

    @classmethod
    async def get_active_tokens_by_user_id(
        cls, db: AsyncSession, user_id: uuid.UUID
    ) -> list["PasswordResetToken"]:
        """Get all active (unused) reset tokens for a user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            List of active PasswordResetToken objects
        """
        result = await db.execute(
            select(cls).where(
                cls.user_id == user_id,
                cls.is_used.is_(False),
            )
        )
        return list(result.scalars().all())

    @classmethod
    async def get_active_by_token_hash(
        cls, db: AsyncSession, token_hash: str
    ) -> "PasswordResetToken | None":
        """Get an active reset token by its hash.

        Args:
            db: Database session
            token_hash: SHA256 hash of the raw token

        Returns:
            PasswordResetToken if found and active, None otherwise
        """
        result = await db.execute(
            select(cls).where(
                cls.token_hash == token_hash,
                cls.is_used.is_(False),
            )
        )
        return result.scalar_one_or_none()
