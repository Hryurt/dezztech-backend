import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import (
    EmailAlreadyVerifiedException,
    EmailNotVerifiedException,
    InvalidCredentialsException,
    OTPAttemptsExceededException,
    OTPExpiredException,
    OTPInvalidException,
    OTPResendTooSoonException,
    PasswordReuseNotAllowedException,
)
from src.auth.models import EmailVerificationCode, PasswordResetToken
from src.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    RegisterStartResponse,
    TokenResponse,
)
from src.auth.utils import create_access_token, generate_otp_code, log_sensitive_debug
from src.logger import get_logger
from src.users.exceptions import (
    UserInactiveException,
    UserNotFoundException,
)
from src.users.models import User, UserRole
from src.users.schemas import UserCreateInternal
from src.users.service import UserService

logger = get_logger(__name__)


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncSession):
        """Initialize AuthService with database session.

        Args:
            db: Database session
        """
        self.db = db

    async def _create_and_log_otp(self, user: User) -> None:
        """Create EmailVerificationCode and log it (no external email integration)."""
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=EmailVerificationCode.OTP_VALIDITY_MINUTES
        )
        code = EmailVerificationCode(
            user_id=user.id,
            code=generate_otp_code(),
            expires_at=expires_at,
            is_used=False,
            attempts_count=0,
        )
        self.db.add(code)
        log_sensitive_debug(f"Email OTP for {user.email}: {code.code}")

    async def create_email_change_otp(self, user: User) -> None:
        """Create email verification OTP for email change flow. Public wrapper for _create_and_log_otp."""
        await self._create_and_log_otp(user)

    async def forgot_password(self, email: str) -> None:
        """Send password reset token for the given email.

        If user does not exist, returns silently (does not leak user existence).

        Args:
            email: User email address
        """
        user = await User.get_by_email(self.db, email)

        if user is None:
            # Do not leak whether the email exists
            return

        # Invalidate all existing active reset tokens for this user
        result = await self.db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.user_id == user.id,
                PasswordResetToken.is_used == False,  # noqa: E712
            )
        )
        existing_tokens = result.scalars().all()

        for token_obj in existing_tokens:
            token_obj.is_used = True

        # Generate new reset token
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=PasswordResetToken.RESET_TOKEN_VALIDITY_MINUTES
        )

        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            is_used=False,
        )
        self.db.add(reset_token)

        # Single commit for invalidation + new token creation
        await self.db.commit()
        await self.db.refresh(reset_token)

        log_sensitive_debug(f"Password reset token for {user.email}: {raw_token}")

    async def reset_password(self, token: str, new_password: str) -> None:
        """Reset user password using a valid reset token.

        Args:
            token: Raw reset token from the reset link
            new_password: New password to set

        Raises:
            OTPInvalidException: If token not found or invalid
            OTPExpiredException: If token has expired
            UserNotFoundException: If user not found
        """
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        result = await self.db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == token_hash,
                PasswordResetToken.is_used == False,  # noqa: E712
            )
        )
        reset_token = result.scalar_one_or_none()

        if reset_token is None:
            raise OTPInvalidException()

        if datetime.now(timezone.utc) > reset_token.expires_at:
            reset_token.is_used = True
            await self.db.commit()
            raise OTPExpiredException()

        user = await User.get_by_id(self.db, reset_token.user_id)

        if user is None:
            raise UserNotFoundException(user_id=reset_token.user_id)

        # Prevent password reuse
        if user.check_password(new_password):
            raise PasswordReuseNotAllowedException()

        user.set_password(new_password)
        reset_token.is_used = True

        await self.db.commit()

        logger.info(f"Password reset successful for user ID: {user.id}")

    async def start_register(self, email: str) -> RegisterStartResponse:
        """Check email existence and return registration status.

        Args:
            email: User email to check

        Returns:
            RegisterStartResponse with ok and already_registered

        Raises:
            EmailAlreadyVerifiedException: If user exists and email already verified
        """
        user = await User.get_by_email(self.db, email)

        if user is None:
            return RegisterStartResponse(ok=True, already_registered=False)

        if user.email_verified_at is not None:
            raise EmailAlreadyVerifiedException(email=email)

        return RegisterStartResponse(ok=True, already_registered=True)

    async def register(self, data: RegisterRequest) -> RegisterResponse:
        """Register a new user and send OTP.

        Args:
            data: Registration data (email, password, first_name, last_name, etc.)

        Returns:
            RegisterResponse with user_id and otp_sent

        Raises:
            EmailAlreadyVerifiedException: If user exists and email already verified
        """
        user_service = UserService(self.db)
        user = await User.get_by_email(self.db, data.email)

        if user:
            if user.email_verified_at:
                raise EmailAlreadyVerifiedException(email=data.email)
            # User exists but not verified - generate new OTP
            await self._create_and_log_otp(user)
            await self.db.commit()
            return RegisterResponse(user_id=user.id, otp_sent=True)

        # Create new user
        user_data = UserCreateInternal(
            email=data.email,
            password=data.password,
            first_name=data.first_name,
            last_name=data.last_name,
            role=UserRole.USER,
            is_active=True,
            phone_number=data.phone_number,
            how_did_you_hear=data.how_did_you_hear,
        )
        user = await user_service.create_user(user_data)

        # Ensure user.id is generated before creating OTP
        await self.db.flush()

        await self._create_and_log_otp(user)

        # Single transaction commit
        await self.db.commit()
        await self.db.refresh(user)
        return RegisterResponse(user_id=user.id, otp_sent=True)

    async def verify_email(self, email: str, code: str) -> dict:
        """Verify email with OTP code.

        Args:
            email: User email
            code: 4-digit OTP code

        Returns:
            Dict with email_verified: True

        Raises:
            UserNotFoundException: If user not found
            OTPInvalidException: If no valid code or code mismatch
            OTPExpiredException: If code expired
            OTPAttemptsExceededException: If max attempts exceeded
        """
        user = await User.get_by_email(self.db, email)
        if not user:
            raise UserNotFoundException(email=email)

        if user.email_verified_at:
            raise EmailAlreadyVerifiedException(email=email)

        verification_code = await EmailVerificationCode.get_latest_active_by_user_id(
            self.db, user.id
        )
        if not verification_code:
            logger.warning(f"No verification code found for {email}")
            raise OTPInvalidException()

        try:
            verification_code.verify_or_raise(code)
        except Exception:
            await self.db.commit()
            raise

        user.email_verified_at = datetime.now(timezone.utc)
        await self.db.commit()
        logger.info(f"Email verified for {user.email} (ID: {user.id})")
        return {"email_verified": True}

    async def resend_otp(self, email: str) -> dict:
        """Resend OTP for email verification.

        Args:
            email: User email

        Returns:
            Dict with otp_sent and optionally cooldown_seconds_remaining

        Raises:
            UserNotFoundException: If user not found
            EmailAlreadyVerifiedException: If email already verified
            OTPResendTooSoonException: If cooldown not elapsed
        """
        user = await User.get_by_email(self.db, email)
        if not user:
            raise UserNotFoundException(email=email)

        if user.email_verified_at:
            raise EmailAlreadyVerifiedException(email=email)

        latest_code = await EmailVerificationCode.get_latest_active_by_user_id(
            self.db, user.id
        )
        if latest_code and not latest_code.can_resend():
            elapsed = (
                datetime.now(timezone.utc) - latest_code.last_sent_at
            ).total_seconds()
            remaining = max(
                0,
                int(EmailVerificationCode.RESEND_COOLDOWN_SECONDS - elapsed),
            )
            raise OTPResendTooSoonException(cooldown_seconds_remaining=remaining)

        await self._create_and_log_otp(user)
        await self.db.commit()
        return {
            "otp_sent": True,
            "cooldown_seconds_remaining": EmailVerificationCode.RESEND_COOLDOWN_SECONDS,
        }

    async def login(self, data: LoginRequest) -> TokenResponse:
        """Authenticate user and return access token.

        Args:
            data: Login credentials (email, password)

        Returns:
            TokenResponse with JWT access token

        Raises:
            InvalidCredentialsException: If user does not exist or password incorrect
            EmailNotVerifiedException: If email not verified
            UserInactiveException: If user is inactive
        """
        user = await User.get_by_email(self.db, data.email)

        if user is None or not user.check_password(data.password):
            logger.warning("Failed login attempt")
            raise InvalidCredentialsException()

        if user.email_verified_at is None:
            logger.warning("Login attempted with unverified email")
            raise EmailNotVerifiedException()

        if not user.is_active:
            logger.warning(f"Inactive user login attempt (ID: {user.id})")
            raise UserInactiveException(user_id=user.id)

        logger.info(f"User logged in (ID: {user.id})")
        access_token = create_access_token(subject=str(user.id))

        return TokenResponse(access_token=access_token, token_type="bearer")

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
