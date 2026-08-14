"""
Department View.
Handles HTTP API requests for department operations.
"""
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from apps.organization.services.department_service import DepartmentService
from apps.organization.serializers.department_serializer import DepartmentSerializer
from apps.common.responses.api_response import ApiResponse


class DepartmentView(APIView):
    """Handle department API requests."""

    def post(self, request):
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            service = DepartmentService()
            result = service.create_department(serializer.validated_data)
            return ApiResponse.success(
                message="Department created successfully.",
                data={"department_id": result},
                status_code=status.HTTP_201_CREATED,
            )
        return ApiResponse.error(
            message=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    def get(self, request, department_id=None):
        if department_id:
            service = DepartmentService()
            department = service.get_department(department_id)
            return ApiResponse.success(
                message="Department fetched successfully.",
                data=department,
                status_code=status.HTTP_200_OK,
            )
        service = DepartmentService()
        departments = service.list_departments()
        return ApiResponse.success(
            message="Departments fetched successfully.",
            data=departments,
            status_code=status.HTTP_200_OK,
        )