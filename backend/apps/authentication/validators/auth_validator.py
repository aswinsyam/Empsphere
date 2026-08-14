"""
Authentication Validator.
Validation logic for authentication.
"""
from __future__ import annotations

from apps.common.exceptions.custom_exception import ValidationException


class AuthValidator:
    """Authentication validation logic."""

    @staticmethod
    def validate_registration(dto):
        """Validate registration DTO."""
        errors = []
        if not dto.first_name or not dto.first_name.strip():
            errors.append("First name is required.")
        if not dto.last_name or not dto.last_name.strip():
            errors.append("Last name is required.")
        if not dto.email or not dto.email.strip():
            errors.append("Email is required.")
        elif "@" not in dto.email:
            errors.append("Valid email is required.")
        if not dto.password or len(dto.password) < 6:
            errors.append("Password must be at least 6 characters.")
        if dto.password != dto.confirm_password:
            errors.append("Passwords do not match.")
        if not dto.company_secret:
            errors.append("Company secret is required.")
        if errors:
            raise ValidationException("\n".join(errors))

    @staticmethod
    def validate_login(dto):
        """Validate login DTO."""
        errors = []
        if not dto.email or not dto.email.strip():
            errors.append("Email is required.")
        if not dto.password or not dto.password.strip():
            errors.append("Password is required.")
        if errors:
            raise ValidationException("\n".join(errors))