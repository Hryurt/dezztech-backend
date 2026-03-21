from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


# Base custom exception class
class AppException(Exception):
    """Base exception class for application-specific exceptions."""

    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_SERVER_ERROR",
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


# HTTP-related exceptions
class BadRequestException(AppException):
    """Exception for 400 Bad Request errors."""

    def __init__(
        self,
        message: str = "Bad request",
        error_code: str = "BAD_REQUEST",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=error_code,
            details=details,
        )


class UnauthorizedException(AppException):
    """Exception for 401 Unauthorized errors."""

    def __init__(
        self,
        message: str = "Unauthorized",
        error_code: str = "UNAUTHORIZED",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=error_code,
            details=details,
        )


class ForbiddenException(AppException):
    """Exception for 403 Forbidden errors."""

    def __init__(
        self,
        message: str = "Forbidden",
        error_code: str = "FORBIDDEN",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code=error_code,
            details=details,
        )


class NotFoundException(AppException):
    """Exception for 404 Not Found errors."""

    def __init__(
        self,
        message: str = "Resource not found",
        error_code: str = "NOT_FOUND",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=error_code,
            details=details,
        )


class ConflictException(AppException):
    """Exception for 409 Conflict errors."""

    def __init__(
        self,
        message: str = "Conflict",
        error_code: str = "CONFLICT",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code=error_code,
            details=details,
        )


class UnprocessableEntityException(AppException):
    """Exception for 422 Unprocessable Entity errors."""

    def __init__(
        self,
        message: str = "Unprocessable entity",
        error_code: str = "UNPROCESSABLE_ENTITY",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code=error_code,
            details=details,
        )


class InternalServerException(AppException):
    """Exception for 500 Internal Server errors."""

    def __init__(
        self,
        message: str = "Internal server error",
        error_code: str = "INTERNAL_SERVER_ERROR",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=error_code,
            details=details,
        )


# Exception handlers
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handler for custom AppException instances."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "error": exc.message,
            "details": exc.details,
            "path": str(request.url),
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handler for FastAPI HTTPException instances."""
    # Generate error_code from status_code if not available
    error_code = f"HTTP_{exc.status_code}"
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": error_code,
            "error": exc.detail,
            "path": str(request.url),
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler for unhandled exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_code": "UNHANDLED_ERROR",
            "error": "An unexpected error occurred",
            "details": {"type": type(exc).__name__, "message": str(exc)},
            "path": str(request.url),
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handler for Pydantic validation errors."""
    errors = []
    for error in exc.errors():
        # Get field name (last element in location path)
        field = error["loc"][-1] if error["loc"] else "unknown"
        error_type = error["type"]

        errors.append(
            {
                "field": field,
                "type": error_type,
                "context": error.get("ctx", {}),
            }
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error_code": "VALIDATION_ERROR",
            "error": "Validation failed",
            "details": {"errors": errors},
            "path": str(request.url),
        },
    )
