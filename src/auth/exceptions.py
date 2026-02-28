from src.core.security.password_policy import PASSWORD_ERROR_MESSAGE
from src.exceptions import (
    AppException,
    BadRequestException,
    ConflictException,
    ForbiddenException,
    UnauthorizedException,
)


class InvalidCredentialsException(UnauthorizedException):
    """Exception raised when login credentials are invalid."""

    def __init__(self):
        super().__init__(
            message="Invalid email or password",
            error_code="INVALID_CREDENTIALS",
            details={},
        )


class TokenExpiredException(UnauthorizedException):
    """Exception raised when JWT token has expired."""

    def __init__(self):
        super().__init__(
            message="Token has expired",
            error_code="TOKEN_EXPIRED",
            details={},
        )


class InvalidTokenException(UnauthorizedException):
    """Exception raised when JWT token is invalid."""

    def __init__(self):
        super().__init__(
            message="Invalid or malformed token",
            error_code="INVALID_TOKEN",
            details={},
        )


class TokenMissingException(UnauthorizedException):
    """Exception raised when JWT token is missing from request."""

    def __init__(self):
        super().__init__(
            message="Authentication token is required",
            error_code="TOKEN_MISSING",
            details={},
        )


class OTPExpiredException(BadRequestException):
    """Exception raised when OTP has expired."""

    def __init__(self):
        super().__init__(
            message="Verification code has expired",
            error_code="OTP_EXPIRED",
            details={},
        )


class OTPInvalidException(BadRequestException):
    """Exception raised when OTP code is invalid."""

    def __init__(self):
        super().__init__(
            message="Invalid verification code",
            error_code="OTP_INVALID",
            details={},
        )


class OTPAttemptsExceededException(BadRequestException):
    """Exception raised when max verification attempts exceeded."""

    def __init__(self):
        super().__init__(
            message="Maximum verification attempts exceeded",
            error_code="OTP_ATTEMPTS_EXCEEDED",
            details={},
        )


class OTPResendTooSoonException(BadRequestException):
    """Exception raised when resend is requested before cooldown."""

    def __init__(self, cooldown_seconds_remaining: int):
        super().__init__(
            message="Please wait before requesting a new code",
            error_code="OTP_RESEND_TOO_SOON",
            details={"cooldown_seconds_remaining": cooldown_seconds_remaining},
        )


class EmailNotVerifiedException(BadRequestException):
    """Exception raised when login attempted with unverified email."""

    def __init__(self, email: str | None = None):
        details = {"email": email} if email else {}
        super().__init__(
            message="Please verify your email before logging in",
            error_code="EMAIL_NOT_VERIFIED",
            details=details,
        )


class EmailAlreadyVerifiedException(ConflictException):
    """Exception raised when email is already verified."""

    def __init__(self, email: str):
        super().__init__(
            message=f"Email {email} is already verified",
            error_code="EMAIL_ALREADY_VERIFIED",
            details={"email": email},
        )


class InsufficientPermissionsException(ForbiddenException):
    """Exception raised when user lacks required permissions."""

    def __init__(self, required_permission: str | None = None):
        details = {}
        if required_permission:
            message = f"Insufficient permissions: '{required_permission}' required"
            details = {"required_permission": required_permission}
        else:
            message = "Insufficient permissions"

        super().__init__(
            message=message,
            error_code="INSUFFICIENT_PERMISSIONS",
            details=details,
        )


class WeakPasswordException(BadRequestException):
    """Exception raised when password does not meet complexity requirements."""

    def __init__(self):
        super().__init__(
            message=PASSWORD_ERROR_MESSAGE,
            error_code="WEAK_PASSWORD",
            details={},
        )


class PasswordReuseNotAllowedException(AppException):
    """Raised when the new password is the same as the current one."""

    def __init__(self) -> None:
        super().__init__(
            error_code="PASSWORD_REUSE_NOT_ALLOWED",
            status_code=400,
            message="New password cannot be the same as the current password",
        )
