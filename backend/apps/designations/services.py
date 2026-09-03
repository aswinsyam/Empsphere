"""
Designation service.
Handles designation business logic.
"""
from __future__ import annotations

import re
from datetime import datetime
from bson import ObjectId

from rest_framework.exceptions import NotFound, ValidationError

from apps.activity_logs.services import log_activity
from apps.common.constants import Collections
from apps.common.database import get_collection


class DesignationService:
    """Designation business logic."""

    def __init__(self):
        self.collection = get_collection(Collections.DESIGNATIONS)
        self._ensure_indexes()

    def _ensure_indexes(self):
        """Create required indexes if they do not exist."""
        existing = {index["name"] for index in self.collection.list_indexes()}
        if "designation_name_unique" not in existing:
            self.collection.create_index(
                [("name", 1)],
                unique=True,
                name="designation_name_unique",
            )
        if "designation_code_unique" not in existing:
            self.collection.create_index(
                [("code", 1)],
                unique=True,
                name="designation_code_unique",
            )

    def create_designation(self, data):
        """Create a new designation."""
        name = data.get("name", "").strip()
        code = data.get("code")
        description = data.get("description")
        created_by = data.get("created_by")

        if not name:
            raise ValidationError("Designation name is required.")

        existing = self.collection.find_one({"name": {"$regex": f"^{re.escape(name)}$", "$options": "i"}})
        if existing:
            raise ValidationError("A designation with this name already exists.")
        if code:
            existing_code = self.collection.find_one({"code": {"$regex": f"^{re.escape(code.strip())}$", "$options": "i"}})
            if existing_code:
                raise ValidationError("A designation with this code already exists.")

        document = {
            "name": name,
            "code": code.strip().upper() if code else None,
            "description": description,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        designation_id = str(self.collection.insert_one(document).inserted_id)
        log_activity(
            "DESIGNATION", "CREATE_DESIGNATION",
            str(created_by), designation_id,
            "SUCCESS", f"Created designation {name}.",
        )
        return self.get_designation(designation_id)

    def get_designation(self, designation_id):
        """Get designation by ID."""
        if not ObjectId.is_valid(designation_id):
            raise NotFound("Designation not found.")
        record = self.collection.find_one({"_id": ObjectId(designation_id)})
        if not record:
            raise NotFound("Designation not found.")
        return self._serialize(record)

    def list_designations(self, search=None, page=1, page_size=10, include_inactive=False):
        """List designations with optional search and pagination."""
        query = {}
        if not include_inactive:
            query["is_active"] = True
        if search:
            query["$or"] = [
                {"name": {"$regex": re.escape(search), "$options": "i"}},
                {"code": {"$regex": re.escape(search), "$options": "i"}},
            ]
        total_records = self.collection.count_documents(query)
        skip = (page - 1) * page_size
        designations = list(self.collection.find(query).skip(skip).limit(page_size))
        total_pages = (total_records + page_size - 1) // page_size if page_size else 1
        return {
            "designations": [self._serialize(d) for d in designations],
            "total_records": total_records,
            "total_pages": total_pages,
            "page": page,
            "page_size": page_size,
        }

    def update_designation(self, designation_id, data):
        """Update a designation."""
        if not data:
            raise ValidationError("No data to update.")
        if data.get("name") is not None and not str(data["name"]).strip():
            raise ValidationError("Designation name cannot be empty.")

        if not ObjectId.is_valid(designation_id):
            raise NotFound("Designation not found.")
        existing = self.collection.find_one({"_id": ObjectId(designation_id)})
        if not existing:
            raise NotFound("Designation not found.")

        updates = {}
        if data.get("name") is not None:
            updates["name"] = data["name"].strip()
        if data.get("code") is not None:
            updates["code"] = data["code"].strip().upper() if data["code"] else None
        if data.get("description") is not None:
            updates["description"] = data["description"]
        if data.get("is_active") is not None:
            updates["is_active"] = data["is_active"]
        if not updates:
            return self._serialize(existing)

        updates["updated_at"] = datetime.utcnow()
        self.collection.update_one(
            {"_id": ObjectId(designation_id)}, {"$set": updates}
        )
        record = self.collection.find_one({"_id": ObjectId(designation_id)})
        log_activity(
            "DESIGNATION", "UPDATE_DESIGNATION",
            str(data.get("updated_by")), str(designation_id),
            "SUCCESS", f"Updated designation {record.get('name')}.",
        )
        return self._serialize(record)

    def _serialize(self, record):
        """Convert a raw MongoDB document into a serialized designation dict."""
        if not record:
            return None
        users_collection = get_collection(Collections.USERS)
        return {
            "designation_id": str(record.get("_id")),
            "name": record.get("name"),
            "code": record.get("code"),
            "description": record.get("description"),
            "is_active": record.get("is_active", True),
            "employee_count": users_collection.count_documents({"designation_id": str(record.get("_id"))}),
            "created_at": record.get("created_at"),
            "updated_at": record.get("updated_at"),
        }
