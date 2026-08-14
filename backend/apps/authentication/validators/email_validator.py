"""
Email Validator.
Email validation logic.
"""
from __future__ import annotations

from apps.common.exceptions.custom_exception import ValidationException


class EmailValidator:
    """Email validation logic."""

    @staticmethod
    def validate_email_format(email):
        """Validate email format."""
        if not email or "@" not in email:
            raise ValidationException("Valid email address is required.")
        return email.strip().lower()