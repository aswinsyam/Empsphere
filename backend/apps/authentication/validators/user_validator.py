"""
User Validator.
User validation logic.
"""
from __future__ import annotations

from apps.common.exceptions.custom_exception import ValidationException, NotFoundException


class UserValidator:
    """User validation logic."""

    @staticmethod
    def validate_user_id(user_id):
        """Validate user ID."""
        if not user_id:
            raise ValidationException("User ID is required.")
        return user_id

    @staticmethod
    def validate_user_exists(user):
        """Validate user exists."""
        if not user:
            raise NotFoundException("User not found.")
        return user