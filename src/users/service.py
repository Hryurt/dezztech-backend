import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import (
    InvalidCredentialsException,
    OTPAttemptsExceededException,
    OTPExpiredException,
    OTPInvalidException,
    PasswordReuseNotAllowedException,
)
from src.auth.models import EmailVerificationCode
from src.logger import get_logger
from src.users.exceptions import (
    LastSuperAdminException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from src.users.models import User, UserRole
from src.exceptions import BadRequestException, ConflictException
from src.users.schemas import (
    DeleteAccountRequest,
    UserChangePasswordRequest,
    UserCreateInternal,
    UserMeUpdateRequest,
)

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
        """Create a new user (does not commit).

        Args:
            data: User creation data

        Returns:
            Created user object (not yet persisted)

        Raises:
            UserAlreadyExistsException: If user with email already exists
        """
        if await User.exists(self.db, data.email):
            logger.warning(f"Attempt to create duplicate user: {data.email}")
            raise UserAlreadyExistsException(email=data.email)

        user = await User.create(self.db, data)

        logger.info(f"User created (pending commit): {user.email} (ID: {user.id})")
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

    async def update_current_user(self, user: User, data: UserMeUpdateRequest) -> User:
        """Update current user's profile fields.

        Args:
            user: User to update
            data: Update data (first_name, last_name, phone_number)

        Returns:
            Updated user object
        """
        if data.first_name is not None:
            user.first_name = data.first_name
        if data.last_name is not None:
            user.last_name = data.last_name
        if data.phone_number is not None:
            user.phone_number = data.phone_number

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def change_password(
        self,
        user: User,
        data: UserChangePasswordRequest,
    ) -> None:
        """Change current user's password.

        Args:
            user: User to update
            data: Password change data (current_password, new_password, confirm_password)

        Raises:
            InvalidCredentialsException: If current_password is incorrect
            PasswordReuseNotAllowedException: If new_password equals current password
        """
        if not user.check_password(data.current_password):
            raise InvalidCredentialsException()

        if data.new_password == data.current_password:
            raise PasswordReuseNotAllowedException()

        user.set_password(data.new_password)
        await self.db.commit()
        await self.db.refresh(user)

    async def deactivate_account(
        self,
        user: User,
        data: DeleteAccountRequest,
    ) -> None:
        """Soft delete (deactivate) the current user account.

        Args:
            user: User to deactivate
            data: Request with current_password for verification

        Raises:
            InvalidCredentialsException: If current_password is incorrect
            LastSuperAdminException: If user is the last active super admin
        """
        if not user.check_password(data.current_password):
            raise InvalidCredentialsException()

        if user.role == UserRole.SUPER_ADMIN:
            active_users = await User.get_active_users(self.db)
            active_super_admins = [u for u in active_users if u.role == UserRole.SUPER_ADMIN]
            if len(active_super_admins) == 1 and active_super_admins[0].id == user.id:
                raise LastSuperAdminException()

        user.deactivate()
        await self.db.commit()

    async def send_password_changed_email(self, user: User) -> None:
        """Send password change notification email.

        Uses same infrastructure as OTP emails. Intended to be run via BackgroundTasks.
        """
        subject = "Your password has been changed"
        body = (
            f"Hello {user.first_name},\n\n"
            "Your password was successfully changed.\n"
            "If this was not you, please contact support immediately."
        )
        logger.info(f"Password change notification to {user.email}\nSubject: {subject}\n{body}")

    async def get_active_users(self) -> list[User]:
        """Get all active users.

        Returns:
            List of active users
        """
        return await User.get_active_users(self.db)

    async def request_email_change(
        self,
        user: User,
        new_email: str,
        current_password: str,
    ) -> None:
        """Request email change by setting pending_email and creating OTP.

        Args:
            user: Current authenticated user
            new_email: New email address
            current_password: Current password for re-authentication

        Raises:
            InvalidCredentialsException: If current_password is incorrect
            BadRequestException: If new email equals current email
            ConflictException: If email already in use (email or pending_email)
        """
        try:
            if not user.check_password(current_password):
                raise InvalidCredentialsException()

            if new_email == user.email:
                raise BadRequestException(
                    message="New email must be different from current email",
                    error_code="SAME_EMAIL",
                    details={},
                )

            if await User.email_or_pending_exists(self.db, new_email):
                logger.warning(f"Email change rejected: {new_email} already in use")
                raise ConflictException(
                    message="Email already in use",
                    error_code="EMAIL_ALREADY_IN_USE",
                    details={"email": new_email},
                )

            user.pending_email = new_email
            from src.auth.service import AuthService

            auth_service = AuthService(self.db)
            await auth_service.create_email_change_otp(user)
            await self.db.commit()
            await self.db.refresh(user)

            logger.info(f"Email change requested for {user.email} (ID: {user.id}) -> {new_email}")
        except Exception:
            await self.db.rollback()
            raise

    async def confirm_email_change(self, user: User, code: str) -> None:
        """Confirm email change by verifying OTP and applying pending_email.

        Args:
            user: Current authenticated user
            code: 4-digit OTP code

        Raises:
            BadRequestException: If no pending email change
            OTPInvalidException: If OTP not found or code mismatch
            OTPExpiredException: If OTP expired
            OTPAttemptsExceededException: If max attempts exceeded
        """
        try:
            if user.pending_email is None:
                raise BadRequestException(
                    message="No email change request found",
                    error_code="NO_PENDING_EMAIL",
                    details={},
                )

            verification_code = await EmailVerificationCode.get_latest_active_by_user_id(
                self.db, user.id
            )
            if not verification_code:
                logger.warning(f"No verification code found for email change (user {user.id})")
                raise OTPInvalidException()

            try:
                verification_code.verify_or_raise(code)
            except Exception:
                await self.db.commit()
                raise

            user.email = user.pending_email
            user.pending_email = None
            user.email_verified_at = datetime.now(timezone.utc)

            await self.db.commit()
            await self.db.refresh(user)

            logger.info(f"Email change confirmed for user {user.id}: -> {user.email}")
        except Exception:
            await self.db.rollback()
            raise
