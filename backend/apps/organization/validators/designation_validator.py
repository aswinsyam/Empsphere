"""
Designation Validator.
Designation validation logic.
"""
from __future__ import annotations

from apps.common.exceptions.custom_exception import ValidationException


class DesignationValidator:
    """Designation validation logic."""

    @staticmethod
    def validate_create(name, code=None):
        """Validate required fields for designation creation."""
        if not name or not str(name).strip():
            raise ValidationException("Designation name is required.")

    @staticmethod
    def validate_update(designation_id, update_data):
        """Validate designation update."""
        if not update_data:
            raise ValidationException("No data to update.")
        name = update_data.get("name")
        if name is not None and not str(name).strip():
            raise ValidationException("Designation name cannot be empty.")
