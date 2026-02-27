import uuid
from datetime import UTC, datetime, timedelta

import jwt
from passlib.context import CryptContext

from src.auth.config import ACCESS_TOKEN_EXPIRE, ALGORITHM, PWD_DEPRECATED, PWD_SCHEMES
from src.auth.constants import (
    CLAIM_EXPIRATION,
    CLAIM_ISSUED_AT,
    CLAIM_SUBJECT,
    CLAIM_TYPE,
    TOKEN_TYPE_ACCESS,
)
from src.config import settings
from src.logger import get_logger

# Password hashing context
pwd_context = CryptContext(schemes=PWD_SCHEMES, deprecated=PWD_DEPRECATED)

# Logger for sensitive debug messages
_logger = get_logger(__name__)


def log_sensitive_debug(message: str) -> None:
    """Log sensitive information only in development environment.

    Use this for logging OTP codes, tokens, and other sensitive values
    that should never appear in non-development logs.

    Args:
        message: The sensitive message to log
    """
    if settings.ENVIRONMENT == "development":
        _logger.debug(message)


def validate_password_strength(password: str) -> None:
    """Validate password meets complexity requirements.

    Delegates to core password policy. Raises WeakPasswordException for domain layer compatibility.

    Args:
        password: Plain text password to validate

    Raises:
        WeakPasswordException: If password does not meet complexity requirements
    """
    from src.auth.exceptions import WeakPasswordException
    from src.core.security.password_policy import validate_password_strength as _validate

    try:
        _validate(password)
    except ValueError as e:
        raise WeakPasswordException() from e


# ==================== Password Hashing ====================


def hash_password(password: str) -> str:
    """Hash a plain password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password from database

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


# ==================== JWT Token Generation ====================


def create_access_token(subject: str | int | uuid.UUID, expires_delta: timedelta | None = None) -> str:
    """Create a new JWT access token.

    Args:
        subject: User identifier (usually user_id or email)
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + ACCESS_TOKEN_EXPIRE

    to_encode = {
        CLAIM_SUBJECT: str(subject),
        CLAIM_TYPE: TOKEN_TYPE_ACCESS,
        CLAIM_EXPIRATION: expire,
        CLAIM_ISSUED_AT: datetime.now(UTC),
    }

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ==================== JWT Token Verification ====================


def decode_token(token: str) -> dict:
    """Decode and verify a JWT token.

    Args:
        token: JWT token string to decode

    Returns:
        Decoded token payload as dictionary

    Raises:
        jwt.ExpiredSignatureError: If token has expired
        jwt.InvalidTokenError: If token is invalid
    """
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    return payload


def verify_access_token(token: str) -> str | None:
    """Verify an access token and return the subject.

    Args:
        token: JWT access token string

    Returns:
        Subject (user identifier) if valid, None otherwise
    """
    try:
        payload = decode_token(token)

        # Check token type
        token_type = payload.get(CLAIM_TYPE)
        if token_type != TOKEN_TYPE_ACCESS:
            return None

        # Get subject
        subject = payload.get(CLAIM_SUBJECT)
        if subject is None:
            return None

        return subject

    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except jwt.InvalidTokenError:
        # Token is invalid
        return None
