"""Centralized password policy validation.

Single source of truth for password rules across the backend.
"""

import re

PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,64}$")

PASSWORD_ERROR_MESSAGE = (
    "Password must be 8–64 characters and include uppercase, lowercase, digit, and special character."
)


def validate_password_strength(password: str) -> None:
    """Validate password meets complexity requirements.

    Args:
        password: Plain text password to validate

    Raises:
        ValueError: If password does not meet complexity requirements
    """
    if not PASSWORD_REGEX.match(password):
        raise ValueError(PASSWORD_ERROR_MESSAGE)
