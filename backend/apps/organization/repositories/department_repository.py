"""
Department Repository.
Handles department database operations.
"""
from __future__ import annotations

import re

from bson import ObjectId
from datetime import datetime

from apps.common.core.collections import Collections
from apps.common.database.mongo import mongo


class DepartmentRepository:
    """Department data access layer for MongoDB operations."""

    def __init__(self):
        self.collection = mongo.get_collection(Collections.DEPARTMENTS)
        self._ensure_indexes()

    def _ensure_indexes(self):
        """Create required indexes if they do not exist."""
        existing = {index["name"] for index in self.collection.list_indexes()}
        if "department_name_unique" not in existing:
            self.collection.create_index(
                [("name", 1)],
                unique=True,
                name="department_name_unique",
            )
        if "department_code_unique" not in existing:
            self.collection.create_index(
                [("code", 1)],
                unique=True,
                name="department_code_unique",
            )

    def create(self, document, user_id):
        """Create a new department record."""
        collection = mongo.get_collection(Collections.DEPARTMENTS)
        document["is_active"] = True
        document["created_at"] = datetime.utcnow()
        document["updated_at"] = datetime.utcnow()
        result = collection.insert_one(document)
        return str(result.inserted_id)

    def get_by_id(self, department_id):
        """Get department by ID (ignores active state; used internally).

        Returns None for a malformed id so callers can raise NotFound
        instead of surfacing a BSON error.
        """
        if not ObjectId.is_valid(department_id):
            return None
        collection = mongo.get_collection(Collections.DEPARTMENTS)
        return collection.find_one({"_id": ObjectId(department_id)})

    def get_all(self, search=None, page=1, page_size=10, include_inactive=False):
        """Get departments with optional search and pagination.

        By default only ``is_active`` departments are returned. Pass
        ``include_inactive=True`` to return all departments regardless of
        active state.
        """
        collection = mongo.get_collection(Collections.DEPARTMENTS)
        query = {}
        if not include_inactive:
            query["is_active"] = True
        if search:
            query["$or"] = [
                {"name": {"$regex": re.escape(search), "$options": "i"}},
                {"code": {"$regex": re.escape(search), "$options": "i"}},
            ]
        total_records = collection.count_documents(query)
        skip = (page - 1) * page_size
        departments = list(collection.find(query).skip(skip).limit(page_size))
        total_pages = (total_records + page_size - 1) // page_size if page_size else 1
        return departments, total_records, total_pages

    def get_by_code(self, code):
        """Get department by code (case-insensitive)."""
        collection = mongo.get_collection(Collections.DEPARTMENTS)
        return collection.find_one({
            "code": {"$regex": f"^{re.escape(code)}$", "$options": "i"}
        })

    def get_by_name(self, name):
        """Get department by name (case-insensitive)."""
        collection = mongo.get_collection(Collections.DEPARTMENTS)
        return collection.find_one({
            "name": {"$regex": f"^{re.escape(name)}$", "$options": "i"}
        })

    def update(self, department_id, updates, user_id):
        """Update a department."""
        collection = mongo.get_collection(Collections.DEPARTMENTS)
        updates["updated_at"] = datetime.utcnow()
        return collection.update_one({"_id": ObjectId(department_id)}, {"$set": updates})

    def soft_delete(self, department_id, user_id):
        """Soft delete a department."""
        collection = mongo.get_collection(Collections.DEPARTMENTS)
        return collection.update_one(
            {"_id": ObjectId(department_id)}, {"$set": {"is_active": False}}
        )

    def count_employees(self, department_id):
        """Count employees assigned to a department."""
        users_collection = mongo.get_collection(Collections.USERS)
        return users_collection.count_documents({"department_id": department_id})
