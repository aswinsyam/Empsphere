"""
Employee Service.
Handles employee business logic.
"""
from __future__ import annotations

from apps.authentication.managers.employee_code_manager import EmployeeCodeManager
from apps.common.base.base_service import BaseService
from apps.common.exceptions.custom_exception import (
    ConflictException,
    ForbiddenException,
    NotFoundException,
)
from apps.common.permissions.role_permission import RolePermission
from apps.common.security.password_manager import PasswordManager
from apps.employee.repositories.employee_repository import EmployeeRepository
from apps.employee.validators.employee_validator import EmployeeValidator


class EmployeeService(BaseService):
    """Employee business logic and orchestration."""

    def __init__(self):
        super().__init__()
        self.repository = EmployeeRepository()
        self.validator = EmployeeValidator()
        self.employee_code_manager = EmployeeCodeManager()
        self.password_manager = PasswordManager()

    def create_employee(self, dto):
        """Create a new employee after validating input."""
        self.validator.validate_create(dto.first_name, dto.last_name, dto.email, dto.role, dto.password)
        if self.repository.get_by_email(dto.email):
            raise ConflictException("Email already exists.")
        employee_code = dto.employee_code or self.employee_code_manager.generate()
        document = {
            "employee_code": employee_code,
            "first_name": dto.first_name,
            "last_name": dto.last_name,
            "full_name": f"{dto.first_name} {dto.last_name}".strip() or None,
            "email": dto.email,
            "phone": (dto.phone or "").strip(),
            "password": self.password_manager.hash_password(dto.password) if dto.password else None,
            "role": dto.role or "EMPLOYEE",
            "department_id": dto.department_id,
            "designation_id": dto.designation_id,
            "joining_date": str(dto.joining_date) if dto.joining_date else None,
            "status": dto.status or "ACTIVE",
            "is_active": True,
            "login_provider": "LOCAL" if dto.password else None,
        }
        employee_id = self.repository.create(document, user_id=dto.created_by)
        self.log_activity(
            module="EMPLOYEE",
            action="CREATE_EMPLOYEE",
            performed_by=str(dto.created_by),
            target_id=str(employee_id),
            status="SUCCESS",
            description=f"Created employee {dto.first_name} {dto.last_name} ({dto.email}).",
        )
        return employee_id

    def get_employee(self, employee_id):
        """Get an employee."""
        employee = self.repository.get_by_id(employee_id)
        if not employee:
            raise NotFoundException("Employee not found.")
        return self._serialize(employee, detail=True)

    def list_employees(self, search=None, department_id=None, status=None, page=1, page_size=10, joining_date_from=None, joining_date_to=None):
        """List employees with filters and pagination."""
        employees, total_records, total_pages = self.repository.get_all(
            search=search,
            department_id=department_id,
            status=status,
            page=page,
            page_size=page_size,
            joining_date_from=joining_date_from,
            joining_date_to=joining_date_to,
        )
        return {
            "employees": [self._serialize(e, detail=False) for e in employees],
            "total_records": total_records,
            "total_pages": total_pages,
            "page": page,
            "page_size": page_size,
        }

    def update_employee(self, employee_id, dto, actor_role=None):
        """Update an employee.

        RBAC: the actor must be able to manage the target employee's role
        (e.g., an HR_MANAGER cannot update an ADMIN). Enforced via
        RolePermission.can_manage_user().
        """
        existing = self.repository.get_by_id(employee_id)
        if not existing:
            raise NotFoundException("Employee not found.")
        update_data = {}
        if dto.first_name not in (None, ""):
            update_data["first_name"] = dto.first_name
        if dto.last_name not in (None, ""):
            update_data["last_name"] = dto.last_name
        if dto.email not in (None, ""):
            update_data["email"] = dto.email
        if dto.phone is not None:
            update_data["phone"] = dto.phone
        if dto.role not in (None, ""):
            update_data["role"] = dto.role
        if dto.department_id is not None:
            update_data["department_id"] = dto.department_id
        if dto.designation_id is not None:
            update_data["designation_id"] = dto.designation_id
        if dto.joining_date is not None:
            update_data["joining_date"] = dto.joining_date
        if dto.status not in (None, ""):
            update_data["status"] = dto.status.upper()
        if dto.employee_code not in (None, ""):
            update_data["employee_code"] = dto.employee_code
        self.validator.validate_update(employee_id, update_data)
        if actor_role:
            target_role = existing.get("role", "EMPLOYEE")
            if not RolePermission.can_manage_user(actor_role, target_role):
                raise ForbiddenException("You do not have permission to update this employee.")
        if not update_data:
            return self._serialize(existing, detail=True)
        self.repository.update(employee_id, update_data, user_id=dto.updated_by)
        employee = self.repository.get_by_id(employee_id)
        self.log_activity(
            module="EMPLOYEE",
            action="UPDATE_EMPLOYEE",
            performed_by=str(dto.updated_by),
            target_id=str(employee_id),
            status="SUCCESS",
            description=f"Updated employee {employee.get('first_name')} {employee.get('last_name')}.",
        )
        return self._serialize(employee, detail=True)

    def delete_employee(self, employee_id, user_id):
        """Delete an employee."""
        existing = self.repository.get_by_id(employee_id)
        if not existing:
            raise NotFoundException("Employee not found.")
        self.repository.soft_delete(employee_id, user_id=user_id)
        self.log_activity(
            module="EMPLOYEE",
            action="DELETE_EMPLOYEE",
            performed_by=str(user_id),
            target_id=str(employee_id),
            status="SUCCESS",
            description=f"Deleted employee {existing.get('first_name')} {existing.get('last_name')}.",
        )

    def update_employee_status(self, employee_id, status, user_id, actor_role=None):
        """Update employee status."""
        existing = self.repository.get_by_id(employee_id)
        if not existing:
            raise NotFoundException("Employee not found.")
        if actor_role:
            target_role = existing.get("role", "EMPLOYEE")
            if not RolePermission.can_manage_user(actor_role, target_role):
                raise ForbiddenException("You do not have permission to update this employee's status.")
        self.validator.validate_status(status)
        self.repository.update(employee_id, {"status": status.upper()}, user_id=user_id)
        employee = self.repository.get_by_id(employee_id)
        action = "ACTIVATE_EMPLOYEE" if status.upper() == "ACTIVE" else "DEACTIVATE_EMPLOYEE"
        self.log_activity(
            module="EMPLOYEE",
            action=action,
            performed_by=str(user_id),
            target_id=str(employee_id),
            status="SUCCESS",
            description=f"Updated employee status to {status.upper()}.",
        )
        return self._serialize(employee, detail=True)

    def _serialize(self, employee, detail=False):
        """Convert a raw MongoDB document into a serialized employee dict."""
        if not employee:
            return None
        serialized = {
            "user_id": str(employee.get("_id")),
            "employee_code": employee.get("employee_code"),
            "first_name": employee.get("first_name"),
            "last_name": employee.get("last_name"),
            "full_name": employee.get("full_name"),
            "email": employee.get("email"),
            "phone": employee.get("phone"),
            "role": employee.get("role"),
            "department_id": employee.get("department_id"),
            "designation_id": employee.get("designation_id"),
            "profile_image_id": str(employee.get("profile_image_id")) if employee.get("profile_image_id") else None,
            "is_email_verified": employee.get("is_email_verified"),
            "login_provider": employee.get("login_provider"),
            "last_login": employee.get("last_login"),
            "is_active": employee.get("is_active"),
            "status": employee.get("status"),
            "joining_date": employee.get("joining_date"),
            "created_at": employee.get("created_at"),
            "updated_at": employee.get("updated_at"),
        }
        if detail:
            serialized["working_duration"] = self._calculate_working_duration(
                employee.get("joining_date")
            )
            serialized["total_working_days"] = self._calculate_total_working_days(
                employee.get("joining_date")
            )
        return serialized

    @staticmethod
    def _calculate_working_duration(joining_date):
        """Calculate human-readable working duration from joining date."""
        if not joining_date:
            return None
        from datetime import datetime
        try:
            start = datetime.strptime(str(joining_date), "%Y-%m-%d")
            now = datetime.utcnow()
            delta = now - start
            years = delta.days // 365
            months = (delta.days % 365) // 30
            days = (delta.days % 365) % 30
            parts = []
            if years:
                parts.append(f"{years} year{'s' if years != 1 else ''}")
            if months:
                parts.append(f"{months} month{'s' if months != 1 else ''}")
            if days or not parts:
                parts.append(f"{days} day{'s' if days != 1 else ''}")
            return ", ".join(parts)
        except Exception:
            return None

    @staticmethod
    def _calculate_total_working_days(joining_date):
        """Calculate total working days from joining date."""
        if not joining_date:
            return None
        from datetime import datetime
        try:
            start = datetime.strptime(str(joining_date), "%Y-%m-%d")
            now = datetime.utcnow()
            return (now - start).days
        except Exception:
            return None
