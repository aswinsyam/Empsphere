"""
Department Service.
Handles department business logic.
"""
from __future__ import annotations

from apps.organization.repositories.department_repository import DepartmentRepository
from apps.organization.dtos.department_dto import DepartmentDTO, DepartmentUpdateDTO
from apps.organization.schemas.department_schema import DepartmentSchema
from apps.organization.validators.department_validator import DepartmentValidator


class DepartmentService:
    """Department business logic."""

    def __init__(self):
        self.repository = DepartmentRepository()
        self.validator = DepartmentValidator()

    def create_department(self, dto):
        """Create a new department."""
        self.validator.validate_create(dto.name, dto.code)
        document = DepartmentSchema.create_document({
            "name": dto.name,
            "code": dto.code,
            "description": dto.description,
            "head_user_id": dto.head_user_id,
            "organization_id": dto.organization_id,
        })
        return self.repository.create(document, user_id=dto.created_by)

    def get_department(self, department_id):
        """Get a department."""
        department = self.repository.get_by_id(department_id)
        if not department:
            raise NotFoundException("Department not found.")
        return self._serialize(department)

    def list_departments(self):
        """List all departments."""
        departments = self.repository.get_all()
        return [self._serialize(d) for d in departments]

    def update_department(self, department_id, dto):
        """Update a department."""
        existing = self.repository.get_by_id(department_id)
        if not existing:
            raise NotFoundException("Department not found.")
        update_data = {}
        if dto.name not in (None, ""):
            update_data["name"] = dto.name
        if dto.code not in (None, ""):
            update_data["code"] = dto.code
        if dto.description is not None:
            update_data["description"] = dto.description
        if dto.head_user_id is not None:
            update_data["head_user_id"] = dto.head_user_id
        if dto.organization_id is not None:
            update_data["organization_id"] = dto.organization_id
        if not update_data:
            return self._serialize(existing)
        self.validator.validate_update(department_id, update_data)
        self.repository.update(department_id, update_data, user_id=dto.updated_by)
        department = self.repository.get_by_id(department_id)
        return self._serialize(department)

    def delete_department(self, department_id, user_id):
        """Delete a department."""
        existing = self.repository.get_by_id(department_id)
        if not existing:
            raise NotFoundException("Department not found.")
        self.repository.soft_delete(department_id, user_id=user_id)

    def _serialize(self, department):
        """Serialize department."""
        return {
            "department_id": str(department.get("_id")),
            "name": department.get("name"),
            "code": department.get("code"),
            "description": department.get("description"),
            "head_user_id": department.get("head_user_id"),
            "organization_id": department.get("organization_id"),
            "is_active": department.get("is_active"),
            "created_at": department.get("created_at"),
            "updated_at": department.get("updated_at"),
        }