"""
Employee Controller.

Exposes RESTful endpoints for employee CRUD.

Authorization: every Employee Management endpoint (list, detail, create,
update, status) is restricted to the existing `EMPLOYEE_MANAGER_ROLES` group
(SUPER_ADMIN, ADMIN, HR_MANAGER) via the shared `@require_role` decorator.
EMPLOYEE has no access to Employee Management and receives the standard 403
response; employees read their own record through the Profile/Auth endpoints.
Delete remains SUPER_ADMIN-only and is no longer exposed in the UI.
"""
from __future__ import annotations

from rest_framework import status
from rest_framework.views import APIView

from apps.common.base.base_controller import BaseController
from apps.common.decorators.permission import require_role
from apps.common.core.roles import EMPLOYEE_MANAGER_ROLES, Role
from apps.employee.dtos.employee_dto import EmployeeDTO, EmployeeUpdateDTO
from apps.employee.serializers.employee_serializer import (
    EmployeeSerializer,
)
from apps.employee.services.employee_service import EmployeeService


class EmployeeController(APIView, BaseController):
    """Employee CRUD endpoints."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.employee_service = EmployeeService()

    @require_role(*EMPLOYEE_MANAGER_ROLES)
    def post(self, request):
        """Create a new employee."""
        serializer = EmployeeSerializer(data=request.data, is_create=True)
        serializer.is_valid(raise_exception=True)

        dto = EmployeeDTO(
            **serializer.validated_data,
            created_by=str(request.user["_id"]),
        )

        employee_id = self.employee_service.create_employee(dto)

        return self.success(
            message="Employee created successfully.",
            data={"user_id": employee_id},
            status_code=status.HTTP_201_CREATED,
        )

    @require_role(*EMPLOYEE_MANAGER_ROLES)
    def get(self, request, employee_id=None):
        """List employees or get a single employee."""
        search = request.query_params.get("search")
        department_id = request.query_params.get("department_id")
        status_filter = request.query_params.get("status")
        joining_date_from = request.query_params.get("joining_date_from")
        joining_date_to = request.query_params.get("joining_date_to")
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))

        if employee_id:
            employee = self.employee_service.get_employee(employee_id)
            return self.success(
                message="Employee fetched successfully.",
                data=employee,
                status_code=status.HTTP_200_OK,
            )

        result = self.employee_service.list_employees(
            search=search,
            department_id=department_id,
            status=status_filter,
            joining_date_from=joining_date_from,
            joining_date_to=joining_date_to,
            page=page,
            page_size=page_size,
        )
        return self.success(
            message="Employees fetched successfully.",
            data=result,
            status_code=status.HTTP_200_OK,
        )

    @require_role(*EMPLOYEE_MANAGER_ROLES)
    def put(self, request, employee_id):
        """Update an employee."""
        serializer = EmployeeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dto = EmployeeUpdateDTO(
            **serializer.validated_data,
            updated_by=str(request.user["_id"]),
        )

        employee = self.employee_service.update_employee(
            employee_id, dto, actor_role=request.user.get("role")
        )

        return self.success(
            message="Employee updated successfully.",
            data=employee,
            status_code=status.HTTP_200_OK,
        )

    @require_role(*EMPLOYEE_MANAGER_ROLES)
    def patch(self, request, employee_id):
        """Update employee status."""
        status_value = request.data.get("status")
        if not status_value:
            return self.error(
                message="Status is required.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        employee = self.employee_service.update_employee_status(
            employee_id, status_value, user_id=str(request.user["_id"]),
            actor_role=request.user.get("role"),
        )
        return self.success(
            message="Employee status updated successfully.",
            data=employee,
            status_code=status.HTTP_200_OK,
        )

    @require_role(Role.SUPER_ADMIN)
    def delete(self, request, employee_id):
        """Delete an employee."""
        self.employee_service.delete_employee(
            employee_id, user_id=str(request.user["_id"])
        )

        return self.success(
            message="Employee deleted successfully.",
            data=None,
            status_code=status.HTTP_200_OK,
        )
