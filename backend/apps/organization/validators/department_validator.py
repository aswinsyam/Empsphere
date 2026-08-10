"""
Department validators.

Business-level validation for department operations.
"""

from __future__ import annotations

from apps.common.exceptions.custom_exception import ConflictException
from apps.organization.repositories.department_repository import (
    DepartmentRepository,
)


class DepartmentValidator:
    """
    Business validation for departments.
    """

    def __init__(self):
        self.department_repository = DepartmentRepository()

    def validate_create(self, name: str, code: str) -> None:
        """
        Ensure a department with the same name/code does not already exist.
        """

        if self.department_repository.name_exists(name):
            raise ConflictException("A department with this name already exists.")

        if self.department_repository.code_exists(code):
            raise ConflictException("A department with this code already exists.")

    def validate_update(self, department_id: str, name: str, code: str) -> None:
        """
        Ensure name/code uniqueness while excluding the current department.
        """

        if self.department_repository.name_exists(name, exclude_id=department_id):
            raise ConflictException("A department with this name already exists.")

        if self.department_repository.code_exists(code, exclude_id=department_id):
            raise ConflictException("A department with this code already exists.")
