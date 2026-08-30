"""
Leave DTOs.
Data transfer objects for leave management.
"""
from __future__ import annotations


class LeaveDTO:
    """Leave data transfer object used during creation."""

    def __init__(
        self,
        employee_id=None,
        start_date=None,
        end_date=None,
        leave_type="ANNUAL",
        reason=None,
        status="PENDING",
        created_by=None,
    ):
        self.employee_id = employee_id
        self.start_date = start_date
        self.end_date = end_date
        self.leave_type = leave_type
        self.reason = reason
        self.status = status
        self.created_by = created_by
