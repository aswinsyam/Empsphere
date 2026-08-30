"""
Amenity Controller.
Exposes RESTful endpoints for office amenity management.
"""
from __future__ import annotations

from rest_framework import status
from rest_framework.views import APIView

from apps.common.base.base_controller import BaseController
from apps.common.decorators.permission import require_role
from apps.common.core.roles import Role
from apps.payment.amenities.amenity_dto import AmenityCreateDTO, AmenityUpdateDTO
from apps.payment.amenities.amenity_serializer import (
    AmenityCreateSerializer,
    AmenityUpdateSerializer,
)
from apps.payment.amenities.amenity_service import AmenityService


class AmenityController(APIView, BaseController):
    """Amenity endpoints for admin management."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.amenity_service = AmenityService()

    @require_role(Role.SUPER_ADMIN, Role.ADMIN)
    def post(self, request):
        """Create a new amenity."""
        serializer = AmenityCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dto = AmenityCreateDTO(
            name=serializer.validated_data["name"],
            description=serializer.validated_data.get("description", ""),
            amount=serializer.validated_data["amount"],
            created_by=str(request.user["_id"]),
        )

        amenity = self.amenity_service.create_amenity(dto)

        return self.success(
            message="Amenity created successfully.",
            data=amenity,
            status_code=status.HTTP_201_CREATED,
        )

    @require_role(Role.SUPER_ADMIN, Role.ADMIN, Role.HR_MANAGER, Role.EMPLOYEE)
    def get(self, request, amenity_id=None):
        """List amenities or get a single amenity."""
        if amenity_id:
            amenity = self.amenity_service.get_active_amenity(amenity_id)
            return self.success(
                message="Amenity fetched successfully.",
                data=amenity,
                status_code=status.HTTP_200_OK,
            )

        include_inactive = request.query_params.get("include_inactive", "false").lower() == "true"
        amenities = self.amenity_service.list_amenities(include_inactive=include_inactive)

        return self.success(
            message="Amenities fetched successfully.",
            data={"amenities": amenities},
            status_code=status.HTTP_200_OK,
        )

    @require_role(Role.SUPER_ADMIN, Role.ADMIN)
    def put(self, request, amenity_id):
        """Update an amenity."""
        serializer = AmenityUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dto = AmenityUpdateDTO(
            name=serializer.validated_data.get("name"),
            description=serializer.validated_data.get("description"),
            amount=serializer.validated_data.get("amount"),
            updated_by=str(request.user["_id"]),
        )

        amenity = self.amenity_service.update_amenity(amenity_id, dto)

        return self.success(
            message="Amenity updated successfully.",
            data=amenity,
            status_code=status.HTTP_200_OK,
        )

    @require_role(Role.SUPER_ADMIN, Role.ADMIN)
    def delete(self, request, amenity_id):
        """Soft delete an amenity."""
        self.amenity_service.delete_amenity(amenity_id, user_id=str(request.user["_id"]))

        return self.success(
            message="Amenity deleted successfully.",
            status_code=status.HTTP_200_OK,
        )
