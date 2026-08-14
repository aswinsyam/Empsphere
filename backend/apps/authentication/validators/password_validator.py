"""
Password Validator.
Password validation logic.
"""
from __future__ import annotations

from apps.common.exceptions.custom_exception import ValidationException


class PasswordValidator:
    """Password validation logic."""

    @staticmethod
    def validate_password_strength(password):
        """Validate password strength."""
        if not password or len(password) < 6:
            raise ValidationException("Password must be at least 6 characters.")
        return password