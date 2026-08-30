"""
Department Service.
Handles department business logic.
"""
from __future__ import annotations

from apps.common.base.base_service import BaseService
from apps.common.exceptions.custom_exception import (
    ConflictException,
    ForbiddenException,
    NotFoundException,
)
from apps.organization.repositories.department_repository import DepartmentRepository
from apps.organization.validators.department_validator import DepartmentValidator


class DepartmentService(BaseService):
    """Department business logic and orchestration."""

    def __init__(self):
        super().__init__()
        self.repository = DepartmentRepository()
        self.validator = DepartmentValidator()

    def create_department(self, dto):
        """Create a new department after validating input."""
        self.validator.validate_create(dto.name, dto.code)
        if self.repository.get_by_name(dto.name):
            raise ConflictException("Department name already exists.")
        if self.repository.get_by_code(dto.code):
            raise ConflictException("Department code already exists.")
        document = {
            "name": dto.name,
            "code": dto.code,
            "description": dto.description,
            "head_user_id": dto.head_user_id,
            "organization_id": dto.organization_id,
        }
        department_id = self.repository.create(document, user_id=dto.created_by)
        self.log_activity(
            module="DEPARTMENT",
            action="CREATE_DEPARTMENT",
            performed_by=str(dto.created_by),
            target_id=str(department_id),
            status="SUCCESS",
            description=f"Created department {dto.name} ({dto.code}).",
        )
        return department_id

    def get_department(self, department_id):
        """Get a department (active only — soft-deleted depts are hidden)."""
        department = self.repository.get_by_id(department_id)
        if not department or not department.get("is_active"):
            raise NotFoundException("Department not found.")
        return self._serialize(department)

    def list_departments(self, search=None, page=1, page_size=10, include_inactive=False):
        """List departments with optional search and pagination."""
        departments, total_records, total_pages = self.repository.get_all(
            search=search, page=page, page_size=page_size, include_inactive=include_inactive
        )
        return {
            "departments": [self._serialize(d) for d in departments],
            "total_records": total_records,
            "total_pages": total_pages,
            "page": page,
            "page_size": page_size,
        }

    def update_department(self, department_id, dto, actor_role=None):
        """Update a department."""
        existing = self.repository.get_by_id(department_id)
        if not existing:
            raise NotFoundException("Department not found.")
        update_data = {}
        if dto.name not in (None, ""):
            existing_name = self.repository.get_by_name(dto.name)
            if existing_name and str(existing_name.get("_id")) != department_id:
                raise ConflictException("Department name already exists.")
            update_data["name"] = dto.name
        if dto.code not in (None, ""):
            existing_code = self.repository.get_by_code(dto.code)
            if existing_code and str(existing_code.get("_id")) != department_id:
                raise ConflictException("Department code already exists.")
            update_data["code"] = dto.code
        if dto.description is not None:
            update_data["description"] = dto.description
        if dto.head_user_id is not None:
            update_data["head_user_id"] = dto.head_user_id
        if dto.organization_id is not None:
            update_data["organization_id"] = dto.organization_id
        if dto.is_active is not None:
            update_data["is_active"] = dto.is_active
        if not update_data:
            return self._serialize(existing)
        self.validator.validate_update(department_id, update_data)
        self.repository.update(department_id, update_data, user_id=dto.updated_by)
        department = self.repository.get_by_id(department_id)
        self.log_activity(
            module="DEPARTMENT",
            action="UPDATE_DEPARTMENT",
            performed_by=str(dto.updated_by),
            target_id=str(department_id),
            status="SUCCESS",
            description=f"Updated department {department.get('name')} ({department.get('code')}).",
        )
        return self._serialize(department)

    def delete_department(self, department_id, user_id, actor_role=None):
        """Delete a department."""
        existing = self.repository.get_by_id(department_id)
        if not existing:
            raise NotFoundException("Department not found.")
        employee_count = self.repository.count_employees(department_id)
        if employee_count > 0:
            raise ForbiddenException(
                "Cannot delete department because employees are assigned to it."
            )
        self.repository.soft_delete(department_id, user_id=user_id)
        self.log_activity(
            module="DEPARTMENT",
            action="DELETE_DEPARTMENT",
            performed_by=str(user_id),
            target_id=str(department_id),
            status="SUCCESS",
            description=f"Deleted department {existing.get('name')} ({existing.get('code')}).",
        )

    def _serialize(self, department):
        """Convert a raw MongoDB document into a serialized department dict."""
        return {
            "department_id": str(department.get("_id")),
            "name": department.get("name"),
            "code": department.get("code"),
            "description": department.get("description"),
            "head_user_id": department.get("head_user_id"),
            "organization_id": department.get("organization_id"),
            "is_active": department.get("is_active"),
            "employee_count": self.repository.count_employees(str(department.get("_id"))),
            "created_at": department.get("created_at"),
            "updated_at": department.get("updated_at"),
        }