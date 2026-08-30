"""
Department Validator.
Department validation logic.
"""
from __future__ import annotations

from apps.common.exceptions.custom_exception import ValidationException


class DepartmentValidator:
    """Department validation logic."""

    @staticmethod
    def validate_create(name, code):
        """Validate required fields for department creation."""
        if not name or not name.strip():
            raise ValidationException("Department name is required.")
        if not code or not code.strip():
            raise ValidationException("Department code is required.")

    @staticmethod
    def validate_update(department_id, update_data):
        """Validate department update."""
        if not update_data:
            raise ValidationException("No data to update.")
        name = update_data.get("name")
        if name and not str(name).strip():
            raise ValidationException("Department name cannot be empty.")