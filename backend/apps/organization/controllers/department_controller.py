"""
Department Controller.

Exposes RESTful endpoints for department CRUD.
"""

from rest_framework import status
from rest_framework.views import APIView

from apps.common.base.base_controller import BaseController
from apps.common.decorators.permission import require_role
from apps.common.core.roles import EMPLOYEE_MANAGER_ROLES
from apps.organization.dtos.department_dto import (
    DepartmentDTO,
    DepartmentUpdateDTO,
)
from apps.organization.serializers.department_serializer import (
    DepartmentSerializer,
    DepartmentUpdateSerializer,
)
from apps.organization.services.department_service import DepartmentService


class DepartmentController(APIView, BaseController):
    """
    Department CRUD endpoints.

    Uses DRF APIView with role-based access decorators.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.department_service = DepartmentService()

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------

    @require_role(*EMPLOYEE_MANAGER_ROLES)
    def post(self, request):
        serializer = DepartmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dto = DepartmentDTO(
            **serializer.validated_data,
            created_by=str(request.user["_id"]),
        )

        department_id = self.department_service.create_department(dto)
        department = self.department_service.get_department(department_id)

        return self.success(
            message="Department created successfully.",
            data=department,
            status_code=status.HTTP_201_CREATED,
        )

    # --------------------------------------------------
    # READ
    # --------------------------------------------------

    @require_role(*EMPLOYEE_MANAGER_ROLES)
    def get(self, request, department_id=None):
        search = request.query_params.get("search")
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))
        include_inactive = str(request.query_params.get("include_inactive", "false")).lower() == "true"

        if department_id:
            department = self.department_service.get_department(department_id)
            return self.success(
                message="Department fetched successfully.",
                data=department,
                status_code=status.HTTP_200_OK,
            )

        result = self.department_service.list_departments(
            search=search, page=page, page_size=page_size, include_inactive=include_inactive
        )
        return self.success(
            message="Departments fetched successfully.",
            data=result,
            status_code=status.HTTP_200_OK,
        )

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------

    @require_role(*EMPLOYEE_MANAGER_ROLES)
    def put(self, request, department_id):
        serializer = DepartmentUpdateSerializer(data=request.data)
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

    @require_role(*EMPLOYEE_MANAGER_ROLES)
    def delete(self, request, department_id):
        self.department_service.delete_department(
            department_id, user_id=str(request.user["_id"]),
            actor_role=request.user.get("role"),
        )

        return self.success(
            message="Department deleted successfully.",
            data=None,
            status_code=status.HTTP_200_OK,
        )
