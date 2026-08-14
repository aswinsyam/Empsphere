"""
Department Repository.
Handles department database operations.
"""
from __future__ import annotations

from bson import ObjectId
from datetime import datetime

from apps.common.core.collections import Collections
from apps.common.database.mongo import mongo


class DepartmentRepository:
    """Department data access layer."""

    def create(self, document, user_id):
        """Create a new department."""
        collection = mongo.get_collection(Collections.DEPARTMENTS)
        document["is_active"] = True
        document["created_at"] = datetime.utcnow()
        document["updated_at"] = datetime.utcnow()
        result = collection.insert_one(document)
        return str(result.inserted_id)

    def get_by_id(self, department_id):
        """Get department by ID."""
        collection = mongo.get_collection(Collections.DEPARTMENTS)
        return collection.find_one({"_id": ObjectId(department_id)})

    def get_all(self):
        """Get all departments."""
        collection = mongo.get_collection(Collections.DEPARTMENTS)
        return list(collection.find())

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
