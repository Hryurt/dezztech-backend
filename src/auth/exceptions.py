from src.exceptions import ForbiddenException, UnauthorizedException


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
