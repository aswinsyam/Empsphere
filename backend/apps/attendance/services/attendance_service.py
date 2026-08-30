"""
Attendance Service.
Handles attendance business logic.

Why this exists:
- Centralizes all attendance rules (marking, updating, summary).
- Keeps the controller thin by moving business logic out of the HTTP layer.
- Validates that employees are active before attendance is recorded.
- Logs important actions for the activity log system.

Data flow:
Controller → Service → Repository → MongoDB
"""
from __future__ import annotations

from datetime import datetime, date

from pymongo.errors import DuplicateKeyError

from apps.authentication.repositories.user_repository import UserRepository
from apps.attendance.repositories.attendance_repository import AttendanceRepository
from apps.attendance.validators.attendance_validator import AttendanceValidator
from apps.common.base.base_service import BaseService
from apps.common.exceptions.custom_exception import ConflictException, ForbiddenException, NotFoundException


class AttendanceService(BaseService):
    """Attendance business logic."""

    def __init__(self):
        super().__init__()
        self.repository = AttendanceRepository()
        self.validator = AttendanceValidator()
        self.user_repository = UserRepository()

    def _to_datetime(self, value):
        """Convert a date or datetime to a datetime object."""
        if isinstance(value, datetime):
            return value
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time())
        return value

    def _to_date_str(self, value):
        """Convert a date or datetime to a date string."""
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        return str(value)

    def mark_attendance(self, dto, user_role=None):
        """Mark attendance for an employee.

        Business rules:
        - EMPLOYEE can only mark their own attendance.
        - Inactive employees cannot have attendance marked.
        - Duplicate attendance for the same employee + date is prevented by MongoDB unique index.
        """
        self.validator.validate_create(dto.employee_id, dto.date)
        self.validator.validate_status(dto.status)
        if user_role == "EMPLOYEE" and str(dto.employee_id) != str(dto.created_by):
            raise ForbiddenException("You can only mark attendance for yourself.")
        employee = self.user_repository.get_by_id(str(dto.employee_id))
        if not employee or not employee.get("is_active"):
            raise ForbiddenException("Cannot mark attendance for an inactive employee.")
        normalized_date = self._to_date_str(dto.date)
        existing = self.repository.get_by_employee_and_date(dto.employee_id, normalized_date)
        if existing:
            raise ConflictException("Attendance already marked for this date.")
        try:
            attendance_id = self.repository.create({
                "employee_id": str(dto.employee_id),
                "date": normalized_date,
                "status": dto.status.upper() if dto.status else "PRESENT",
                "check_in": self._to_datetime(dto.check_in) if dto.check_in else None,
                "check_out": self._to_datetime(dto.check_out) if dto.check_out else None,
                "remarks": dto.remarks,
            }, user_id=dto.created_by)
        except DuplicateKeyError:
            raise ConflictException("Attendance already marked for this date.")
        self.log_activity(
            module="ATTENDANCE",
            action="CREATE_ATTENDANCE",
            performed_by=str(dto.created_by),
            target_id=str(attendance_id),
            status="SUCCESS",
            description=f"Marked attendance for employee {dto.employee_id} on {normalized_date}.",
        )
        return attendance_id

    def check_in(self, employee_id, user_role=None):
        """Check in an employee for today.

        Business rules:
        - Inactive employees cannot check in.
        - Duplicate check-in for the same day is prevented.
        - Server-side timestamp is used.
        """
        employee = self.user_repository.get_by_id(str(employee_id))
        if not employee or not employee.get("is_active"):
            raise ForbiddenException("Cannot check in an inactive employee.")
        today = datetime.utcnow().date().isoformat()
        existing = self.repository.get_by_employee_and_date(employee_id, today)
        if existing:
            if existing.get("check_in"):
                raise ConflictException("You have already checked in for today.")
            attendance_id = str(existing["_id"])
            self.repository.update(attendance_id, {"check_in": datetime.utcnow()}, user_id=str(employee_id))
            record = self.repository.get_by_id(attendance_id)
            self.log_activity(
                module="ATTENDANCE",
                action="CHECK_IN",
                performed_by=str(employee_id),
                target_id=attendance_id,
                status="SUCCESS",
                description=f"Employee {employee_id} checked in on {today}.",
            )
            return self._serialize(record)
        attendance_id = self.repository.create({
            "employee_id": str(employee_id),
            "date": today,
            "status": "PRESENT",
            "check_in": datetime.utcnow(),
            "check_out": None,
            "remarks": None,
        }, user_id=str(employee_id))
        record = self.repository.get_by_id(attendance_id)
        self.log_activity(
            module="ATTENDANCE",
            action="CHECK_IN",
            performed_by=str(employee_id),
            target_id=attendance_id,
            status="SUCCESS",
            description=f"Employee {employee_id} checked in on {today}.",
        )
        return self._serialize(record)

    def check_out(self, employee_id, user_role=None):
        """Check out an employee for today.

        Business rules:
        - EMPLOYEE can only check out themselves.
        - Inactive employees cannot check out.
        - Employee must have checked in first.
        - Duplicate check-out is prevented.
        - Server-side timestamp is used.
        """
        employee = self.user_repository.get_by_id(str(employee_id))
        if not employee or not employee.get("is_active"):
            raise ForbiddenException("Cannot check out an inactive employee.")
        today = datetime.utcnow().date().isoformat()
        existing = self.repository.get_by_employee_and_date(employee_id, today)
        if not existing:
            raise NotFoundException("You have not checked in for today.")
        if not existing.get("check_in"):
            raise ForbiddenException("You must check in before checking out.")
        if existing.get("check_out"):
            raise ConflictException("You have already checked out for today.")
        attendance_id = str(existing["_id"])
        self.repository.update(attendance_id, {"check_out": datetime.utcnow()}, user_id=str(employee_id))
        record = self.repository.get_by_id(attendance_id)
        self.log_activity(
            module="ATTENDANCE",
            action="CHECK_OUT",
            performed_by=str(employee_id),
            target_id=attendance_id,
            status="SUCCESS",
            description=f"Employee {employee_id} checked out on {today}.",
        )
        return self._serialize(record)

    def get_attendance(self, attendance_id):
        """Get attendance by ID."""
        record = self.repository.get_by_id(attendance_id)
        if not record:
            raise NotFoundException("Attendance record not found.")
        return self._serialize(record)

    def list_attendance(self, employee_id=None, start_date=None, end_date=None, status=None, page=1, page_size=10):
        """List attendance records with filters."""
        records, total_records, total_pages = self.repository.get_all(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            status=status,
            page=page,
            page_size=page_size,
        )
        return {
            "attendance": [self._serialize(r) for r in records],
            "total_records": total_records,
            "total_pages": total_pages,
            "page": page,
            "page_size": page_size,
        }

    def update_attendance(self, attendance_id, dto, user_role=None):
        """Update attendance.

        Only HR_MANAGER, ADMIN, and SUPER_ADMIN can update attendance.
        The controller enforces this role check before calling this method.
        """
        existing = self.repository.get_by_id(attendance_id)
        if not existing:
            raise NotFoundException("Attendance record not found.")
        update_data = {}
        if dto.status:
            self.validator.validate_status(dto.status)
            update_data["status"] = dto.status.upper()
        if dto.check_in is not None:
            update_data["check_in"] = dto.check_in
        if dto.check_out is not None:
            update_data["check_out"] = dto.check_out
        if dto.remarks is not None:
            update_data["remarks"] = dto.remarks
        if not update_data:
            return self._serialize(existing)
        self.repository.update(attendance_id, update_data, user_id=dto.updated_by)
        record = self.repository.get_by_id(attendance_id)
        self.log_activity(
            module="ATTENDANCE",
            action="UPDATE_ATTENDANCE",
            performed_by=str(dto.updated_by),
            target_id=str(attendance_id),
            status="SUCCESS",
            description=f"Updated attendance for employee {existing.get('employee_id')} on {existing.get('date')}.",
        )
        return self._serialize(record)

    def get_attendance_summary(self, employee_id, start_date=None, end_date=None):
        """Get attendance summary for an employee.

        Returns counts of present, absent, half_day, and leave days
        within the optional date range.
        """
        records, _, _ = self.repository.get_all(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            page=1,
            page_size=100000,
        )
        summary = {
            "total_days": len(records),
            "present_days": sum(1 for r in records if r.get("status") == "PRESENT"),
            "absent_days": sum(1 for r in records if r.get("status") == "ABSENT"),
            "half_days": sum(1 for r in records if r.get("status") == "HALF_DAY"),
            "leave_days": sum(1 for r in records if r.get("status") == "LEAVE"),
        }
        summary["attendance_percentage"] = (
            round((summary["present_days"] / summary["total_days"]) * 100, 2)
            if summary["total_days"] > 0
            else 0
        )
        return summary

    def _serialize(self, record):
        """Convert a raw MongoDB document into a serialized attendance dict."""
        if not record:
            return None
        return {
            "attendance_id": str(record.get("_id")),
            "employee_id": record.get("employee_id"),
            "date": record.get("date"),
            "status": record.get("status"),
            "check_in": record.get("check_in"),
            "check_out": record.get("check_out"),
            "remarks": record.get("remarks"),
            "created_at": record.get("created_at"),
            "updated_at": record.get("updated_at"),
        }
