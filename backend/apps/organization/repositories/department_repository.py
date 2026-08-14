"""
Department Repository.
Handles department database operations.
"""
from __future__ import annotations

from apps.organization.schemas.department_schema import DepartmentSchema


class DepartmentRepository:
    """Department data access layer."""

    def create(self, document, user_id):
        """Create a new department."""
        from apps.common.database.mongo import mongo
        collection = mongo.get_collection(Collections.DEPARTMENTS)
        document["is_active"] = True
        document["created_at"] = datetime.utcnow()
        document["updated_at"] = datetime.utcnow()
        return collection.insert_one(document).inserted_id

    def get_by_id(self, department_id):
        """Get department by ID."""
        from apps.common.database.mongo import mongo
        collection = mongo.get_collection(Collections.DEPARTMENTS)
        return collection.find_one({"_id": department_id})

    def get_all(self):
        """Get all departments."""
        from apps.common.database.mongo import mongo
        collection = mongo.get_collection(Collections.DEPARTMENTS)
        return list(collection.find())

    def update(self, department_id, updates, user_id):
        """Update a department."""
        from apps.common.database.mongo import mongo
        collection = mongo.get_collection(Collections.DEPARTMENTS)
        updates["updated_at"] = datetime.utcnow()
        return collection.update_one({"_id": department_id}, {"$set": updates})

    def soft_delete(self, department_id, user_id):
        """Soft delete a department."""
        from apps.common.database.mongo import mongo
        collection = mongo.get_collection(Collections.DEPARTMENTS)
        return collection.update_one(
            {"_id": department_id}, {"$set": {"is_active": False}}
        )