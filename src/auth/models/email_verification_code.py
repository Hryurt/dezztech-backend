import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Uuid,
    desc,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models import TimestampMixin


class EmailVerificationCode(Base, TimestampMixin):
    """Email verification OTP code for user email verification."""

    __tablename__ = "email_verification_codes"

    MAX_ATTEMPTS = 5
    RESEND_COOLDOWN_SECONDS = 60
    OTP_VALIDITY_MINUTES = 10

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    code: Mapped[str] = mapped_column(String(4), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    attempts_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", lazy="selectin")

    # ──────────────────────────────────────────────
    # Domain Methods (Instance Methods)
    # ──────────────────────────────────────────────

    def is_expired(self) -> bool:
        """Return True if current time is greater than expires_at."""
        now = datetime.now(timezone.utc)
        return now > self.expires_at

    def can_resend(self) -> bool:
        """Return True if 60 seconds have passed since last_sent_at."""
        now = datetime.now(timezone.utc)
        elapsed = (now - self.last_sent_at).total_seconds()
        return elapsed >= self.RESEND_COOLDOWN_SECONDS

    def increment_attempts(self) -> None:
        """Increment attempts_count by 1."""
        self.attempts_count += 1

    def has_exceeded_attempts(self) -> bool:
        """Return True if attempts_count >= 5."""
        return self.attempts_count >= self.MAX_ATTEMPTS

    def mark_as_used(self) -> None:
        """Set is_used to True."""
        self.is_used = True

    def verify_or_raise(self, input_code: str) -> None:
        """Verify the provided OTP code.

        Raises appropriate exceptions if invalid.
        Does NOT commit or rollback.
        """
        from src.auth.exceptions import (
            OTPAttemptsExceededException,
            OTPExpiredException,
            OTPInvalidException,
        )

        if self.has_exceeded_attempts():
            raise OTPAttemptsExceededException()

        if self.is_expired():
            raise OTPExpiredException()

        if self.code != input_code:
            self.increment_attempts()
            raise OTPInvalidException()

        self.mark_as_used()

    # ──────────────────────────────────────────────
    # Query Methods (Class Methods)
    # ──────────────────────────────────────────────

    @classmethod
    async def get_latest_active_by_user_id(
        cls, db: AsyncSession, user_id: uuid.UUID
    ) -> Optional["EmailVerificationCode"]:
        """Get the latest unused verification code for a user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Latest EmailVerificationCode if found, None otherwise
        """
        result = await db.execute(
            select(cls)
            .where(cls.user_id == user_id, cls.is_used == False)  # noqa: E712
            .order_by(desc(cls.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()
