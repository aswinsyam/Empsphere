"""
Leave Service.
Handles leave business logic.

Why this exists:
- Centralizes all leave rules (apply, approve, reject, list).
- Keeps the controller thin by moving business logic out of the HTTP layer.
- Validates dates, types, and permissions before touching the database.
- Logs important actions for the activity log system.

Data flow:
Controller → Service → Repository → MongoDB
"""
from __future__ import annotations

from apps.authentication.repositories.user_repository import UserRepository
from apps.leave.repositories.leave_repository import LeaveRepository
from apps.leave.validators.leave_validator import LeaveValidator
from apps.common.base.base_service import BaseService
from apps.common.exceptions.custom_exception import (
    ForbiddenException,
    NotFoundException,
    ValidationException,
)


class LeaveService(BaseService):
    """Leave business logic."""

    def __init__(self):
        super().__init__()
        self.repository = LeaveRepository()
        self.validator = LeaveValidator()
        self.user_repository = UserRepository()

    def apply_leave(self, dto, user_role=None):
        """Apply for leave.

        Business rules:
        - EMPLOYEE can only apply for their own leaves.
        - The employee must be active.
        - Leave dates and type are validated before creation.
        - All new leaves start with status PENDING.
        """
        self.validator.validate_dates(dto.start_date, dto.end_date)
        self.validator.validate_type(dto.leave_type)
        if user_role == "EMPLOYEE" and str(dto.employee_id) != str(dto.created_by):
            raise ForbiddenException("You can only apply for your own leaves.")
        employee = self.user_repository.get_by_id(str(dto.employee_id))
        if not employee or not employee.get("is_active"):
            raise ForbiddenException("Cannot apply leave for an inactive employee.")
        leave_id = self.repository.create({
            "employee_id": str(dto.employee_id),
            "start_date": str(dto.start_date),
            "end_date": str(dto.end_date),
            "leave_type": dto.leave_type.upper() if dto.leave_type else "ANNUAL",
            "reason": dto.reason,
            "status": "PENDING",
        }, user_id=dto.created_by)
        self.log_activity(
            module="LEAVE",
            action="APPLY_LEAVE",
            performed_by=str(dto.created_by),
            target_id=str(leave_id),
            status="SUCCESS",
            description=f"Leave applied for employee {dto.employee_id} from {dto.start_date} to {dto.end_date}.",
        )
        return leave_id

    def get_leave(self, leave_id):
        """Get leave by ID."""
        record = self.repository.get_by_id(leave_id)
        if not record:
            raise NotFoundException("Leave record not found.")
        return self._serialize(record)

    def list_leaves(self, employee_id=None, status=None, leave_type=None, start_date=None, end_date=None, page=1, page_size=10):
        """List leave records with filters."""
        records, total_records, total_pages = self.repository.get_all(
            employee_id=employee_id,
            status=status,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size,
        )
        return {
            "leaves": [self._serialize(r) for r in records],
            "total_records": total_records,
            "total_pages": total_pages,
            "page": page,
            "page_size": page_size,
        }

    def update_leave_status(self, leave_id, status, user_id):
        """Approve or reject leave."""
        self.validator.validate_status(status)
        existing = self.repository.get_by_id(leave_id)
        if not existing:
            raise NotFoundException("Leave record not found.")
        if existing.get("status") != "PENDING":
            raise ValidationException("Only pending leaves can be updated.")
        if str(existing.get("employee_id")) == str(user_id):
            raise ForbiddenException("You cannot approve or reject your own leave.")
        updates = {"status": status.upper()}
        if status.upper() == "APPROVED":
            updates["approved_by"] = user_id
            updates["rejected_by"] = None
        elif status.upper() == "REJECTED":
            updates["rejected_by"] = user_id
            updates["approved_by"] = None
        self.repository.update(leave_id, updates, user_id=user_id)
        record = self.repository.get_by_id(leave_id)
        action = "APPROVE_LEAVE" if status.upper() == "APPROVED" else "REJECT_LEAVE"
        self.log_activity(
            module="LEAVE",
            action=action,
            performed_by=str(user_id),
            target_id=str(leave_id),
            status="SUCCESS",
            description=f"Leave {status.upper()} for employee {existing.get('employee_id')}.",
        )
        return self._serialize(record)

    def _serialize(self, record):
        """Convert a raw MongoDB document into a serialized leave dict."""
        if not record:
            return None
        employee = self.user_repository.get_by_id(record.get("employee_id")) if record.get("employee_id") else None
        employee_name = None
        employee_code = None
        email = None
        if employee:
            first_name = employee.get("first_name", "")
            last_name = employee.get("last_name", "")
            employee_name = f"{first_name} {last_name}".strip() or None
            employee_code = employee.get("employee_code")
            email = employee.get("email")
        return {
            "leave_id": str(record.get("_id")),
            "employee_id": record.get("employee_id"),
            "employee_name": employee_name,
            "employee_code": employee_code,
            "email": email,
            "start_date": record.get("start_date"),
            "end_date": record.get("end_date"),
            "leave_type": record.get("leave_type"),
            "reason": record.get("reason"),
            "status": record.get("status"),
            "approved_by": record.get("approved_by"),
            "rejected_by": record.get("rejected_by"),
            "created_at": record.get("created_at"),
            "updated_at": record.get("updated_at"),
        }
