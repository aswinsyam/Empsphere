"""
Role Validator.
Role validation logic.
"""
from __future__ import annotations

from apps.common.exceptions.custom_exception import ValidationException


class RoleValidator:
    """Role validation logic."""

    @staticmethod
    def validate_role(role):
        """Validate role."""
        valid_roles = ["EMPLOYEE", "HR_MANAGER", "ADMIN", "SUPER_ADMIN"]
        if role not in valid_roles:
            raise ValidationException(f"Invalid role. Must be one of: {', '.join(valid_roles)}")
        return role