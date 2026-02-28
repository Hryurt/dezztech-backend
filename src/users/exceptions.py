import uuid

from src.exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
)


class UserNotFoundException(NotFoundException):
    """Exception raised when a user is not found."""

    def __init__(self, user_id: uuid.UUID | None = None, email: str | None = None):
        if user_id:
            message = f"User with id {user_id} not found"
            details = {"user_id": str(user_id)}
        elif email:
            message = f"User with email {email} not found"
            details = {"email": email}
        else:
            message = "User not found"
            details = {}

        super().__init__(
            message=message,
            error_code="USER_NOT_FOUND",
            details=details,
        )


class UserAlreadyExistsException(ConflictException):
    """Exception raised when a user with the same email already exists."""

    def __init__(self, email: str):
        super().__init__(
            message=f"User with email {email} already exists",
            error_code="USER_ALREADY_EXISTS",
            details={"email": email},
        )


class LastSuperAdminException(BadRequestException):
    """Exception raised when trying to deactivate the last super admin."""

    def __init__(self):
        super().__init__(
            message="Cannot deactivate the last super admin",
            error_code="LAST_SUPER_ADMIN",
            details={},
        )


class UserInactiveException(ForbiddenException):
    """Exception raised when trying to perform action on inactive (deactivated) user."""

    def __init__(self, user_id: uuid.UUID | None = None):
        super().__init__(
            message="User account is deactivated",
            error_code="USER_INACTIVE",
            details={"user_id": str(user_id)} if user_id else {},
        )
