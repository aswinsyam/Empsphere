from __future__ import annotations

from rest_framework import status
from rest_framework.views import APIView

from apps.common.permissions import require_role
from apps.common.responses import success, error
from apps.employees.serializers import EmployeeSerializer
from apps.employees.services import EmployeeService


class EmployeeView(APIView):
    """Employee CRUD endpoints."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.employee_service = EmployeeService()

    @require_role("SUPER_ADMIN", "ADMIN", "HR_MANAGER")
    def post(self, request):
        """Create a new employee."""
        serializer = EmployeeSerializer(data=request.data, is_create=True)
        serializer.is_valid(raise_exception=True)

        data = dict(serializer.validated_data)
        data["created_by"] = str(request.user["_id"])

        employee_id = self.employee_service.create_employee(data)

        return success("Employee created.", {"user_id": employee_id}, status_code=status.HTTP_201_CREATED)

    @require_role("SUPER_ADMIN", "ADMIN", "HR_MANAGER")
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
            return success(data=employee)

        result = self.employee_service.list_employees(
            search=search,
            department_id=department_id,
            status=status_filter,
            joining_date_from=joining_date_from,
            joining_date_to=joining_date_to,
            page=page,
            page_size=page_size,
            actor_role=request.user.get("role"),
        )
        return success(data=result)

    @require_role("SUPER_ADMIN", "ADMIN", "HR_MANAGER")
    def put(self, request, employee_id):
        """Update an employee."""
        serializer = EmployeeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = dict(serializer.validated_data)
        data["updated_by"] = str(request.user["_id"])

        employee = self.employee_service.update_employee(
            employee_id, data, actor_role=request.user.get("role")
        )

        return success(data=employee)

    @require_role("SUPER_ADMIN", "ADMIN", "HR_MANAGER")
    def patch(self, request, employee_id):
        """Update employee status."""
        status_value = request.data.get("status")
        if not status_value:
            return error("Status is required.", status_code=status.HTTP_400_BAD_REQUEST)
        employee = self.employee_service.update_employee_status(
            employee_id, status_value, user_id=str(request.user["_id"]),
            actor_role=request.user.get("role"),
        )
        return success(data=employee)

    @require_role("SUPER_ADMIN")
    def delete(self, request, employee_id):
        """Delete an employee."""
        self.employee_service.delete_employee(
            employee_id, user_id=str(request.user["_id"])
        )

        return success("Employee deleted.")
