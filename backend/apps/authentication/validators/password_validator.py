"""
Password validation helpers.
"""

from apps.common.core.regex import is_valid_password
from apps.common.exceptions.custom_exception import ValidationException


def validate_password(value: str) -> str:
    """Validate password strength."""
    # Bcrypt (used by our password hasher) only supports passwords up to
    # 72 bytes. Reject passwords that exceed this when UTF-8 encoded so
    # callers receive a clear validation error instead of an internal
    # server error during hashing.
    if len(value.encode("utf-8")) > 72:
        raise ValidationException(
            "Password is too long. Maximum allowed length is 72 bytes (UTF-8)."
        )

    if not is_valid_password(value):
        raise ValidationException(
            "Password must be at least 8 characters with uppercase, "
            "lowercase and a number."
        )

    return value
