"""
Attendance DTOs.
Data transfer objects for attendance.
"""
from __future__ import annotations


class AttendanceDTO:
    """Attendance data transfer object used during creation."""

    def __init__(
        self,
        employee_id=None,
        date=None,
        status="PRESENT",
        check_in=None,
        check_out=None,
        remarks=None,
        created_by=None,
    ):
        self.employee_id = employee_id
        self.date = date
        self.status = status
        self.check_in = check_in
        self.check_out = check_out
        self.remarks = remarks
        self.created_by = created_by


class AttendanceUpdateDTO:
    """Attendance data transfer object used during update."""

    def __init__(
        self,
        status=None,
        check_in=None,
        check_out=None,
        remarks=None,
        updated_by=None,
    ):
        self.status = status
        self.check_in = check_in
        self.check_out = check_out
        self.remarks = remarks
        self.updated_by = updated_by
