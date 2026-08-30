"""
Leave Validator.
Leave validation logic.
"""
from __future__ import annotations

from apps.common.exceptions.custom_exception import ValidationException


class LeaveValidator:
    """Leave validation logic."""

    VALID_STATUSES = {"PENDING", "APPROVED", "REJECTED"}
    VALID_TYPES = {"ANNUAL", "SICK", "CASUAL", "UNPAID"}

    @staticmethod
    def validate_status(status):
        """Validate leave status."""
        if status and status.upper() not in LeaveValidator.VALID_STATUSES:
            raise ValidationException(
                f"Invalid status. Must be one of: {', '.join(LeaveValidator.VALID_STATUSES)}."
            )

    @staticmethod
    def validate_type(leave_type):
        """Validate leave type."""
        if leave_type and leave_type.upper() not in LeaveValidator.VALID_TYPES:
            raise ValidationException(
                f"Invalid leave type. Must be one of: {', '.join(LeaveValidator.VALID_TYPES)}."
            )

    @staticmethod
    def validate_dates(start_date, end_date):
        """Validate leave dates."""
        if start_date and end_date and start_date > end_date:
            raise ValidationException("Start date cannot be after end date.")
