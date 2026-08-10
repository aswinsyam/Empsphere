"""
Email validation helpers.
"""

from apps.common.core.regex import is_valid_email
from apps.common.exceptions.custom_exception import ValidationException


def validate_email(value: str) -> str:
    """Validate and normalize an email address."""
    value = (value or "").strip().lower()

    if not is_valid_email(value):
        raise ValidationException("Please provide a valid email address.")

    return value
