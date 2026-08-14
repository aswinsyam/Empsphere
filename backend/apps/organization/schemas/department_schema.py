"""
Department Schema.
MongoDB schema definitions for department.
"""
from __future__ import annotations
from datetime import datetime
from apps.common.database.mongo import mongo
from apps.common.core.collections import Collections


class DepartmentSchema:
    """Department MongoDB schema."""

    @staticmethod
    def create_document(document):
        """Create a department document."""
        collection = mongo.get_collection(Collections.DEPARTMENTS)
        document["is_active"] = True
        document["created_at"] = datetime.utcnow()
        document["updated_at"] = datetime.utcnow()
        collection.insert_one(document)
        return document.get("_id")