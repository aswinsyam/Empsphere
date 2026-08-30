"""
Amenity Repository.
Handles office amenity database operations.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from bson import ObjectId

from apps.common.database.mongo import mongo
from apps.common.core.collections import Collections


class AmenityRepository:
    """Amenity data access layer for MongoDB operations."""

    def __init__(self):
        self.collection = mongo.get_collection(Collections.AMENITIES)
        self._ensure_indexes()

    def _ensure_indexes(self):
        """Create required indexes if they do not exist."""
        existing = {index["name"] for index in self.collection.list_indexes()}
        if "amenity_name_unique" not in existing:
            self.collection.create_index(
                [("name", 1)],
                unique=True,
                name="amenity_name_unique",
            )

    def create(self, document: dict[str, Any], user_id: str) -> str:
        """Create a new amenity record."""
        document["is_active"] = True
        document["created_at"] = datetime.utcnow()
        document["updated_at"] = datetime.utcnow()
        document["created_by"] = user_id
        result = self.collection.insert_one(document)
        return str(result.inserted_id)

    def get_by_id(self, amenity_id: str) -> dict[str, Any] | None:
        """Get amenity by ID."""
        if not ObjectId.is_valid(amenity_id):
            return None
        return self.collection.find_one({"_id": ObjectId(amenity_id)})

    def get_by_name(self, name: str) -> dict[str, Any] | None:
        """Get amenity by name (case-insensitive)."""
        return self.collection.find_one({
            "name": {"$regex": f"^{name.strip()}$", "$options": "i"}
        })

    def get_active_by_id(self, amenity_id: str) -> dict[str, Any] | None:
        """Get active amenity by ID."""
        if not ObjectId.is_valid(amenity_id):
            return None
        return self.collection.find_one({
            "_id": ObjectId(amenity_id),
            "is_active": True,
        })

    def get_all(self, include_inactive: bool = False) -> list[dict[str, Any]]:
        """Get all amenities."""
        query: dict[str, Any] = {}
        if not include_inactive:
            query["is_active"] = True
        return list(self.collection.find(query).sort("name", 1))

    def get_all_paginated(
        self,
        page: int = 1,
        page_size: int = 10,
        include_inactive: bool = False,
    ) -> tuple[list[dict[str, Any]], int, int]:
        """Get all amenities with pagination."""
        query: dict[str, Any] = {}
        if not include_inactive:
            query["is_active"] = True

        total_records = self.collection.count_documents(query)
        skip = (page - 1) * page_size
        records = list(
            self.collection.find(query)
            .sort("name", 1)
            .skip(skip)
            .limit(page_size)
        )
        total_pages = (total_records + page_size - 1) // page_size if page_size else 1
        return records, total_records, total_pages

    def update(self, amenity_id: str, updates: dict[str, Any], user_id: str) -> dict[str, Any] | None:
        """Update amenity."""
        updates["updated_at"] = datetime.utcnow()
        updates["updated_by"] = user_id
        self.collection.update_one(
            {"_id": ObjectId(amenity_id)}, {"$set": updates}
        )
        return self.get_by_id(amenity_id)

    def soft_delete(self, amenity_id: str, user_id: str):
        """Soft delete amenity by setting is_active to False."""
        self.collection.update_one(
            {"_id": ObjectId(amenity_id)},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow(), "updated_by": user_id}},
        )
