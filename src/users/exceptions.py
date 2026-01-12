from src.exceptions import ConflictException, NotFoundException


class UserNotFoundException(NotFoundException):
    """Exception raised when a user is not found."""

    def __init__(self, user_id: int | None = None, email: str | None = None):
        if user_id:
            message = f"User with id {user_id} not found"
            details = {"user_id": user_id}
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


class UserInactiveException(ConflictException):
    """Exception raised when trying to perform action on inactive user."""

    def __init__(self, user_id: int):
        super().__init__(
            message=f"User with id {user_id} is inactive",
            error_code="USER_INACTIVE",
            details={"user_id": user_id},
        )
