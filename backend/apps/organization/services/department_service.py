"""
Department Service.

Handles department business logic.
"""

from __future__ import annotations

from apps.common.base.base_service import BaseService
from apps.common.exceptions.custom_exception import NotFoundException
from apps.organization.dtos.department_dto import (
    DepartmentDTO,
    DepartmentUpdateDTO,
)
from apps.organization.repositories.department_repository import (
    DepartmentRepository,
)
from apps.organization.schemas.department_schema import DepartmentSchema
from apps.organization.validators.department_validator import (
    DepartmentValidator,
)


class DepartmentService(BaseService):
    """
    Business logic for department CRUD operations.
    """

    def __init__(self):
        super().__init__()
        self.department_repository = DepartmentRepository()
        self.validator = DepartmentValidator()

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------

    def create_department(self, dto: DepartmentDTO) -> str:
        """
        Create a new department and return its id.
        """

        self.validator.validate_create(dto.name, dto.code)

        document = DepartmentSchema.create_document(
            {
                "name": dto.name,
                "code": dto.code,
                "description": dto.description,
                "head_user_id": dto.head_user_id,
                "organization_id": dto.organization_id,
                "created_by": dto.created_by,
            }
        )

        department_id = self.department_repository.create(
            document, user_id=dto.created_by
        )

        self.log_activity(
            module="ORGANIZATION",
            action="CREATE",
            performed_by=dto.created_by,
            target_id=department_id,
            status="SUCCESS",
            description=f"Department {dto.name} created.",
        )

        return department_id

    # --------------------------------------------------
    # READ
    # --------------------------------------------------

    def get_department(self, department_id: str) -> dict:
        """
        Return a single department.
        """

        department = self.department_repository.get_by_id(department_id)

        if not department:
            raise NotFoundException("Department not found.")

        return self._serialize(department)

    def list_departments(self) -> list:
        """
        Return all departments.
        """

        departments = self.department_repository.get_all()

        return [self._serialize(department) for department in departments]

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------

    def update_department(
        self, department_id: str, dto: DepartmentUpdateDTO
    ) -> dict:
        """
        Update an existing department.
        """

        existing = self.department_repository.get_by_id(department_id)

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

        self.validator.validate_update(
            department_id,
            update_data.get("name", existing.get("name")),
            update_data.get("code", existing.get("code")),
        )

        self.department_repository.update(
            department_id, update_data, user_id=dto.updated_by
        )

        department = self.department_repository.get_by_id(department_id)

        self.log_activity(
            module="ORGANIZATION",
            action="UPDATE",
            performed_by=dto.updated_by,
            target_id=department_id,
            status="SUCCESS",
            description="Department updated.",
        )

        return self._serialize(department)

    # --------------------------------------------------
    # DELETE
    # --------------------------------------------------

    def delete_department(self, department_id: str, user_id: str | None) -> None:
        """
        Soft delete a department.
        """

        existing = self.department_repository.get_by_id(department_id)

        if not existing:
            raise NotFoundException("Department not found.")

        self.department_repository.soft_delete(department_id, user_id=user_id)

        self.log_activity(
            module="ORGANIZATION",
            action="DELETE",
            performed_by=user_id,
            target_id=department_id,
            status="SUCCESS",
            description=f"Department {existing.get('name')} deleted.",
        )

    # --------------------------------------------------
    # HELPERS
    # --------------------------------------------------

    @staticmethod
    def _serialize(department: dict) -> dict:
        """
        Return a clean department dictionary.
        """

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
