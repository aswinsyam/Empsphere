"""
Designation Controller.

Exposes RESTful endpoints for designation CRUD.
"""
from __future__ import annotations

from rest_framework import status
from rest_framework.views import APIView

from apps.common.base.base_controller import BaseController
from apps.common.decorators.permission import require_role
from apps.common.core.roles import EMPLOYEE_MANAGER_ROLES
from apps.organization.dtos.designation_dto import (
    DesignationDTO,
    DesignationUpdateDTO,
)
from apps.organization.serializers.designation_serializer import (
    DesignationSerializer,
    DesignationUpdateSerializer,
)
from apps.organization.services.designation_service import DesignationService


class DesignationController(APIView, BaseController):
    """
    Designation CRUD endpoints.

    Uses DRF APIView with role-based access decorators.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.designation_service = DesignationService()

    @require_role(*EMPLOYEE_MANAGER_ROLES)
    def post(self, request):
        serializer = DesignationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dto = DesignationDTO(
            **serializer.validated_data,
            created_by=str(request.user["_id"]),
        )

        designation = self.designation_service.create_designation(dto)

        return self.success(
            message="Designation created successfully.",
            data=designation,
            status_code=status.HTTP_201_CREATED,
        )

    @require_role(*EMPLOYEE_MANAGER_ROLES)
    def get(self, request, designation_id=None):
        search = request.query_params.get("search")
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))
        include_inactive = str(request.query_params.get("include_inactive", "false")).lower() == "true"

        if designation_id:
            designation = self.designation_service.get_designation(designation_id)
            return self.success(
                message="Designation fetched successfully.",
                data=designation,
                status_code=status.HTTP_200_OK,
            )

        result = self.designation_service.list_designations(
            search=search, page=page, page_size=page_size, include_inactive=include_inactive
        )
        return self.success(
            message="Designations fetched successfully.",
            data=result,
            status_code=status.HTTP_200_OK,
        )

    @require_role(*EMPLOYEE_MANAGER_ROLES)
    def put(self, request, designation_id):
        serializer = DesignationUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dto = DesignationUpdateDTO(
            **serializer.validated_data,
            updated_by=str(request.user["_id"]),
        )

        designation = self.designation_service.update_designation(designation_id, dto)

        return self.success(
            message="Designation updated successfully.",
            data=designation,
            status_code=status.HTTP_200_OK,
        )
