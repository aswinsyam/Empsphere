"""
Role validation helpers.
"""

from apps.common.core.roles import ROLE_LOOKUP
from apps.common.exceptions.custom_exception import ValidationException


def validate_role(value: str) -> str:
    """Validate that a role string is a known role name."""
    role = (value or "").strip().upper()

    if role not in ROLE_LOOKUP:
        raise ValidationException(f"Invalid role: {value}")

    return role
