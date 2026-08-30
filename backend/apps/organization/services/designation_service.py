"""
Designation Service.
Handles designation business logic.
"""
from __future__ import annotations

from apps.organization.repositories.designation_repository import DesignationRepository
from apps.organization.validators.designation_validator import DesignationValidator
from apps.common.base.base_service import BaseService
from apps.common.exceptions.custom_exception import ConflictException, NotFoundException


class DesignationService(BaseService):
    """Designation business logic."""

    def __init__(self):
        super().__init__()
        self.repository = DesignationRepository()
        self.validator = DesignationValidator()

    def create_designation(self, dto):
        """Create a new designation."""
        self.validator.validate_create(dto.name, dto.code)
        existing = self.repository.get_by_name(dto.name)
        if existing:
            raise ConflictException("A designation with this name already exists.")
        if dto.code:
            existing_code = self.repository.get_by_code(dto.code)
            if existing_code:
                raise ConflictException("A designation with this code already exists.")
        designation_id = self.repository.create({
            "name": dto.name.strip(),
            "code": dto.code.strip().upper() if dto.code else None,
            "description": dto.description,
        }, user_id=dto.created_by)
        self.log_activity(
            module="ORGANIZATION",
            action="CREATE_DESIGNATION",
            performed_by=str(dto.created_by),
            target_id=str(designation_id),
            status="SUCCESS",
            description=f"Created designation {dto.name}.",
        )
        return self.get_designation(designation_id)

    def get_designation(self, designation_id):
        """Get designation by ID."""
        record = self.repository.get_by_id(designation_id)
        if not record:
            raise NotFoundException("Designation not found.")
        return self._serialize(record)

    def list_designations(self, search=None, page=1, page_size=10, include_inactive=False):
        """List designations with optional search and pagination."""
        designations, total_records, total_pages = self.repository.get_all(
            search=search, page=page, page_size=page_size, include_inactive=include_inactive
        )
        return {
            "designations": [self._serialize(d) for d in designations],
            "total_records": total_records,
            "total_pages": total_pages,
            "page": page,
            "page_size": page_size,
        }

    def update_designation(self, designation_id, dto):
        """Update a designation."""
        self.validator.validate_update(designation_id, {
            "name": dto.name,
            "code": dto.code,
            "description": dto.description,
            "is_active": dto.is_active,
        })
        existing = self.repository.get_by_id(designation_id)
        if not existing:
            raise NotFoundException("Designation not found.")
        update_data = {}
        if dto.name is not None:
            update_data["name"] = dto.name.strip()
        if dto.code is not None:
            update_data["code"] = dto.code.strip().upper() if dto.code else None
        if dto.description is not None:
            update_data["description"] = dto.description
        if dto.is_active is not None:
            update_data["is_active"] = dto.is_active
        if not update_data:
            return self._serialize(existing)
        self.repository.update(designation_id, update_data, user_id=dto.updated_by)
        record = self.repository.get_by_id(designation_id)
        self.log_activity(
            module="ORGANIZATION",
            action="UPDATE_DESIGNATION",
            performed_by=str(dto.updated_by),
            target_id=str(designation_id),
            status="SUCCESS",
            description=f"Updated designation {record.get('name')}.",
        )
        return self._serialize(record)

    def _serialize(self, record):
        """Convert a raw MongoDB document into a serialized designation dict."""
        if not record:
            return None
        return {
            "designation_id": str(record.get("_id")),
            "name": record.get("name"),
            "code": record.get("code"),
            "description": record.get("description"),
            "is_active": record.get("is_active", True),
            "employee_count": self.repository.count_employees(str(record.get("_id"))),
            "created_at": record.get("created_at"),
            "updated_at": record.get("updated_at"),
        }
