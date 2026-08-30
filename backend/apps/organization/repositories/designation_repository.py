"""
Designation Repository.
Handles designation database operations.
"""
from __future__ import annotations

import re

from bson import ObjectId
from datetime import datetime

from apps.common.core.collections import Collections
from apps.common.database.mongo import mongo


class DesignationRepository:
    """Designation data access layer for MongoDB operations."""

    def __init__(self):
        self.collection = mongo.get_collection(Collections.DESIGNATIONS)
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

    def create(self, document, user_id):
        """Create a new designation record."""
        document["is_active"] = True
        document["created_at"] = datetime.utcnow()
        document["updated_at"] = datetime.utcnow()
        result = self.collection.insert_one(document)
        return str(result.inserted_id)

    def get_by_id(self, designation_id):
        """Get designation by ID."""
        if not ObjectId.is_valid(designation_id):
            return None
        return self.collection.find_one({"_id": ObjectId(designation_id)})

    def get_all(self, search=None, page=1, page_size=10, include_inactive=False):
        """Get designations with optional search and pagination."""
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
        return designations, total_records, total_pages

    def get_by_code(self, code):
        """Get designation by code (case-insensitive)."""
        return self.collection.find_one({
            "code": {"$regex": f"^{re.escape(code)}$", "$options": "i"}
        })

    def get_by_name(self, name):
        """Get designation by name (case-insensitive)."""
        return self.collection.find_one({
            "name": {"$regex": f"^{re.escape(name)}$", "$options": "i"}
        })

    def update(self, designation_id, updates, user_id):
        """Update a designation."""
        updates["updated_at"] = datetime.utcnow()
        return self.collection.update_one(
            {"_id": ObjectId(designation_id)}, {"$set": updates}
        )

    def count_employees(self, designation_id):
        """Count employees assigned to a designation."""
        users_collection = mongo.get_collection(Collections.USERS)
        return users_collection.count_documents({"designation_id": designation_id})
