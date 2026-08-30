"""
Amenity Service.
Handles office amenity business logic.
"""
from __future__ import annotations

from apps.common.base.base_service import BaseService
from apps.common.exceptions.custom_exception import (
    ConflictException,
    NotFoundException,
    ValidationException,
)
from apps.payment.amenities.amenity_dto import AmenityCreateDTO, AmenityUpdateDTO
from apps.payment.amenities.amenity_repository import AmenityRepository


class AmenityService(BaseService):
    """Office amenity business logic and orchestration."""

    def __init__(self):
        super().__init__()
        self.repository = AmenityRepository()

    def create_amenity(self, dto: AmenityCreateDTO) -> dict:
        """Create a new amenity after validating input."""
        if not dto.name or not dto.name.strip():
            raise ValidationException("Amenity name is required.")
        if dto.amount is None or float(dto.amount) <= 0:
            raise ValidationException("Amount must be a positive number.")

        existing = self.repository.get_by_name(dto.name)
        if existing:
            raise ConflictException("An amenity with this name already exists.")

        document = {
            "name": dto.name.strip(),
            "description": dto.description or "",
            "amount": float(dto.amount),
        }
        amenity_id = self.repository.create(document, user_id=dto.created_by)

        self.log_activity(
            module="AMENITY",
            action="AMENITY_CREATED",
            performed_by=str(dto.created_by),
            target_id=str(amenity_id),
            status="SUCCESS",
            description=f"Created amenity: {dto.name} (₹{dto.amount}).",
        )
        return self._serialize(self.repository.get_by_id(amenity_id))

    def get_amenity(self, amenity_id: str) -> dict:
        """Get an amenity by ID."""
        amenity = self.repository.get_by_id(amenity_id)
        if not amenity:
            raise NotFoundException("Amenity not found.")
        return self._serialize(amenity)

    def get_active_amenity(self, amenity_id: str) -> dict:
        """Get an active amenity by ID."""
        amenity = self.repository.get_active_by_id(amenity_id)
        if not amenity:
            raise NotFoundException("Amenity not found or inactive.")
        return self._serialize(amenity)

    def list_amenities(self, include_inactive: bool = False) -> list[dict]:
        """List all amenities."""
        records = self.repository.get_all(include_inactive=include_inactive)
        return [self._serialize(a) for a in records]

    def list_amenities_paginated(
        self,
        page: int = 1,
        page_size: int = 10,
        include_inactive: bool = False,
    ) -> dict:
        """List amenities with pagination."""
        records, total_records, total_pages = self.repository.get_all_paginated(
            page=page,
            page_size=page_size,
            include_inactive=include_inactive,
        )
        return {
            "amenities": [self._serialize(a) for a in records],
            "total_records": total_records,
            "total_pages": total_pages,
            "page": page,
            "page_size": page_size,
        }

    def update_amenity(self, amenity_id: str, dto: AmenityUpdateDTO) -> dict:
        """Update an amenity."""
        amenity = self.repository.get_by_id(amenity_id)
        if not amenity:
            raise NotFoundException("Amenity not found.")

        updates = {}
        if dto.name is not None:
            updates["name"] = dto.name.strip()
        if dto.description is not None:
            updates["description"] = dto.description
        if dto.amount is not None:
            if float(dto.amount) <= 0:
                raise ValidationException("Amount must be a positive number.")
            updates["amount"] = float(dto.amount)

        self.repository.update(amenity_id, updates, user_id=dto.updated_by)
        return self._serialize(self.repository.get_by_id(amenity_id))

    def delete_amenity(self, amenity_id: str, user_id: str):
        """Soft delete an amenity."""
        amenity = self.repository.get_by_id(amenity_id)
        if not amenity:
            raise NotFoundException("Amenity not found.")

        self.repository.soft_delete(amenity_id, user_id=user_id)
        self.log_activity(
            module="AMENITY",
            action="AMENITY_DELETED",
            performed_by=str(user_id),
            target_id=str(amenity_id),
            status="SUCCESS",
            description=f"Deleted amenity: {amenity.get('name')}.",
        )

    def _serialize(self, amenity: dict) -> dict:
        """Convert a raw MongoDB document into a serialized amenity dict."""
        if not amenity:
            return None
        return {
            "amenity_id": str(amenity.get("_id")),
            "name": amenity.get("name"),
            "description": amenity.get("description"),
            "amount": amenity.get("amount"),
            "is_active": amenity.get("is_active", True),
            "created_at": amenity.get("created_at"),
            "updated_at": amenity.get("updated_at"),
        }
