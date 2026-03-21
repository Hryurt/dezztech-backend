import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.auth.models.email_verification_code import EmailVerificationCode
from src.domains.auth.models.password_reset_token import PasswordResetToken


class AuthRepository:
    """Repository for Auth-related database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── EmailVerificationCode ──

    async def create_verification_code(
        self,
        user_id: uuid.UUID,
        code: str,
        expires_at: datetime,
    ) -> EmailVerificationCode:
        """Create a new email verification code for a user."""
        verification_code = EmailVerificationCode(
            user_id=user_id,
            code=code,
            expires_at=expires_at,
            is_used=False,
            attempts_count=0,
        )
        self.db.add(verification_code)
        return verification_code

    async def get_latest_active_verification_code(
        self, user_id: uuid.UUID
    ) -> Optional[EmailVerificationCode]:
        """Get the latest unused verification code for a user."""
        result = await self.db.execute(
            select(EmailVerificationCode)
            .where(
                EmailVerificationCode.user_id == user_id,
                EmailVerificationCode.is_used.is_(False),
            )
            .order_by(desc(EmailVerificationCode.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

    # ── PasswordResetToken ──

    async def create_reset_token(
        self,
        user_id: uuid.UUID,
        token_hash: str,
        expires_at: datetime,
    ) -> PasswordResetToken:
        """Create a new password reset token for a user."""
        token = PasswordResetToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            is_used=False,
        )
        self.db.add(token)
        return token

    async def get_active_reset_token(
        self, token_hash: str
    ) -> Optional[PasswordResetToken]:
        """Get an active reset token by its hash."""
        result = await self.db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == token_hash,
                PasswordResetToken.is_used.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def invalidate_active_tokens(self, user_id: uuid.UUID) -> None:
        """Invalidate all active (unused) reset tokens for a user."""
        result = await self.db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.is_used.is_(False),
            )
        )
        for token in result.scalars().all():
            token.mark_as_used()
