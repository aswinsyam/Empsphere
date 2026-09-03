"""
Department views — REST endpoints for department CRUD.
"""
from __future__ import annotations

from rest_framework import status
from rest_framework.views import APIView

from apps.common.permissions import require_role
from apps.common.responses import error, success
from apps.departments.serializers import (
    DepartmentSerializer,
    DepartmentUpdateSerializer,
)
from apps.departments.services import DepartmentService


class DepartmentView(APIView):
    """Department CRUD endpoints."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = DepartmentService()

    @require_role("SUPER_ADMIN", "ADMIN", "HR_MANAGER")
    def post(self, request):
        serializer = DepartmentSerializer(data=request.data)
        if not serializer.is_valid():
            return error("Validation error.", errors=serializer.errors)
        data = dict(serializer.validated_data)
        data["created_by"] = str(request.user["_id"])
        dept_id = self.service.create_department(data)
        dept = self.service.get_department(dept_id)
        return success("Department created successfully.", data=dept, status_code=status.HTTP_201_CREATED)

    @require_role("SUPER_ADMIN", "ADMIN", "HR_MANAGER")
    def get(self, request, department_id=None):
        search = request.query_params.get("search")
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))
        include_inactive = (
            str(request.query_params.get("include_inactive", "false")).lower() == "true"
        )

        if department_id:
            return success(
                "Department retrieved successfully.",
                data=self.service.get_department(department_id),
            )

        result = self.service.list_departments(
            search=search, page=page, page_size=page_size, include_inactive=include_inactive
        )
        return success("Departments retrieved successfully.", data=result)

    @require_role("SUPER_ADMIN", "ADMIN", "HR_MANAGER")
    def put(self, request, department_id):
        serializer = DepartmentUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error("Validation error.", errors=serializer.errors)
        data = dict(serializer.validated_data)
        data["updated_by"] = str(request.user["_id"])
        dept = self.service.update_department(department_id, data)
        return success("Department updated successfully.", data=dept)

    @require_role("SUPER_ADMIN", "ADMIN", "HR_MANAGER")
    def delete(self, request, department_id):
        self.service.delete_department(
            department_id, user_id=str(request.user["_id"])
        )
        return success("Department deleted successfully.")
