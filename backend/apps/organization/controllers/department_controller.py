"""
Department Controller.

Exposes RESTful endpoints for department CRUD.
"""

from rest_framework import status
from rest_framework.views import APIView

from apps.common.base.base_controller import BaseController
from apps.common.decorators.permission import require_role
from apps.common.core.roles import Role
from apps.organization.dtos.department_dto import (
    DepartmentDTO,
    DepartmentUpdateDTO,
)
from apps.organization.serializers.department_serializer import (
    DepartmentSerializer,
)
from apps.organization.services.department_service import DepartmentService


class DepartmentController(APIView, BaseController):
    """
    Department endpoints.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.department_service = DepartmentService()

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------

    @require_role(Role.ADMIN, Role.SUPER_ADMIN)
    def post(self, request):
        serializer = DepartmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dto = DepartmentDTO(
            **serializer.validated_data,
            created_by=str(request.user["_id"]),
        )

        department_id = self.department_service.create_department(dto)

        return self.success(
            message="Department created successfully.",
            data={"department_id": department_id},
            status_code=status.HTTP_201_CREATED,
        )

    # --------------------------------------------------
    # READ
    # --------------------------------------------------

    @require_role(Role.HR_MANAGER, Role.ADMIN, Role.SUPER_ADMIN)
    def get(self, request, department_id=None):
        if department_id:
            department = self.department_service.get_department(department_id)
            return self.success(
                message="Department fetched successfully.",
                data=department,
                status_code=status.HTTP_200_OK,
            )

        departments = self.department_service.list_departments()
        return self.success(
            message="Departments fetched successfully.",
            data=departments,
            status_code=status.HTTP_200_OK,
        )

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------

    @require_role(Role.ADMIN, Role.SUPER_ADMIN)
    def put(self, request, department_id):
        serializer = DepartmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dto = DepartmentUpdateDTO(
            **serializer.validated_data,
            updated_by=str(request.user["_id"]),
        )

        department = self.department_service.update_department(department_id, dto)

        return self.success(
            message="Department updated successfully.",
            data=department,
            status_code=status.HTTP_200_OK,
        )

    # --------------------------------------------------
    # DELETE
    # --------------------------------------------------

    @require_role(Role.SUPER_ADMIN)
    def delete(self, request, department_id):
        self.department_service.delete_department(
            department_id, user_id=str(request.user["_id"])
        )

        return self.success(
            message="Department deleted successfully.",
            data=None,
            status_code=status.HTTP_200_OK,
        )
