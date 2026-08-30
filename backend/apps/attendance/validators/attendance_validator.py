"""
Attendance Validator.
Attendance validation logic.
"""
from __future__ import annotations

from apps.common.exceptions.custom_exception import ValidationException


class AttendanceValidator:
    """Attendance validation logic."""

    VALID_STATUSES = {"PRESENT", "ABSENT", "HALF_DAY", "LEAVE"}

    @staticmethod
    def validate_status(status):
        """Validate attendance status."""
        if status and status.upper() not in AttendanceValidator.VALID_STATUSES:
            raise ValidationException(
                f"Invalid status. Must be one of: {', '.join(AttendanceValidator.VALID_STATUSES)}."
            )

    @staticmethod
    def validate_create(employee_id, date):
        """Validate required fields for attendance creation."""
        if not employee_id:
            raise ValidationException("Employee ID is required.")
        if not date:
            raise ValidationException("Date is required.")
