"""
Employee Validator.
Employee validation logic.
"""
from __future__ import annotations

import re

from apps.common.exceptions.custom_exception import (
    ValidationException,
)


class EmployeeValidator:
    """Employee validation logic."""

    VALID_ROLES = {"SUPER_ADMIN", "ADMIN", "HR_MANAGER", "EMPLOYEE"}
    PHONE_PATTERN = re.compile(r"^[+]?[\d\s\-()]{7,15}$")
    EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    @staticmethod
    def validate_create(first_name, last_name, email, role, password=None):
        """Validate required fields for employee creation."""
        if not first_name or not first_name.strip():
            raise ValidationException("First name is required.")
        if not last_name or not last_name.strip():
            raise ValidationException("Last name is required.")
        if not email or not email.strip():
            raise ValidationException("Email is required.")
        if not EmployeeValidator.EMAIL_PATTERN.match(email.strip()):
            raise ValidationException("Enter a valid email address.")
        if not password or not str(password).strip():
            raise ValidationException("Password is required.")
        if len(str(password)) < 8:
            raise ValidationException("Password must be at least 8 characters.")
        if role and role not in EmployeeValidator.VALID_ROLES:
            raise ValidationException(
                f"Invalid role. Must be one of: {', '.join(sorted(EmployeeValidator.VALID_ROLES))}."
            )

    @staticmethod
    def validate_phone(phone):
        """Validate phone number format if provided."""
        if not phone:
            return
        if not EmployeeValidator.PHONE_PATTERN.match(phone):
            raise ValidationException(
                "Enter a valid phone number (digits, spaces, hyphens, parentheses, and leading + allowed)."
            )

    @staticmethod
    def validate_status(status):
        """Validate employee status."""
        valid_statuses = {"ACTIVE", "INACTIVE"}
        if status and status.upper() not in valid_statuses:
            raise ValidationException(
                f"Invalid status. Must be one of: {', '.join(valid_statuses)}."
            )

    @staticmethod
    def validate_update(employee_id, update_data):
        """Validate employee update."""
        if not update_data:
            raise ValidationException("No data to update.")
        if update_data.get("status"):
            EmployeeValidator.validate_status(update_data.get("status"))
        if update_data.get("role"):
            role = update_data.get("role")
            if role not in EmployeeValidator.VALID_ROLES:
                raise ValidationException(
                    f"Invalid role. Must be one of: {', '.join(sorted(EmployeeValidator.VALID_ROLES))}."
                )
        if update_data.get("phone"):
            EmployeeValidator.validate_phone(update_data.get("phone"))
