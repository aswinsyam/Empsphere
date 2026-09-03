"""
Designation views — REST endpoints for designation CRUD.
"""
from __future__ import annotations

from rest_framework import status
from rest_framework.views import APIView

from apps.common.permissions import require_role
from apps.common.responses import error, success
from apps.designations.serializers import (
    DesignationSerializer,
    DesignationUpdateSerializer,
)
from apps.designations.services import DesignationService


class DesignationView(APIView):
    """
    Designation CRUD endpoints.

    Uses DRF APIView with role-based access decorators.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.designation_service = DesignationService()

    @require_role("SUPER_ADMIN", "ADMIN", "HR_MANAGER")
    def post(self, request):
        serializer = DesignationSerializer(data=request.data)
        if not serializer.is_valid():
            return error("Validation error.", errors=serializer.errors)
        data = dict(serializer.validated_data)
        data["created_by"] = str(request.user["_id"])
        designation = self.designation_service.create_designation(data)
        return success("Designation created successfully.", data=designation, status_code=status.HTTP_201_CREATED)

    @require_role("SUPER_ADMIN", "ADMIN", "HR_MANAGER")
    def get(self, request, designation_id=None):
        search = request.query_params.get("search")
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))
        include_inactive = str(request.query_params.get("include_inactive", "false")).lower() == "true"

        if designation_id:
            designation = self.designation_service.get_designation(designation_id)
            return success("Designation retrieved successfully.", data=designation)

        result = self.designation_service.list_designations(
            search=search, page=page, page_size=page_size, include_inactive=include_inactive
        )
        return success("Designations retrieved successfully.", data=result)

    @require_role("SUPER_ADMIN", "ADMIN", "HR_MANAGER")
    def put(self, request, designation_id):
        serializer = DesignationUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error("Validation error.", errors=serializer.errors)
        data = dict(serializer.validated_data)
        data["updated_by"] = str(request.user["_id"])
        designation = self.designation_service.update_designation(designation_id, data)
        return success("Designation updated successfully.", data=designation)
