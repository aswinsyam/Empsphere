"""
Department Repository.

Contains department-specific database operations.
"""

from __future__ import annotations

from bson import ObjectId

from apps.common.base.base_repository import BaseRepository
from apps.common.core.collections import Collections


class DepartmentRepository(BaseRepository):
    """
    Repository for the departments collection.
    """

    COLLECTION_NAME = Collections.DEPARTMENTS

    def __init__(self):
        super().__init__(self.COLLECTION_NAME)

    def name_exists(self, name: str, exclude_id: str | None = None) -> bool:
        """
        Check whether a department name already exists.
        """
        filters = {"name": name.strip()}
        if exclude_id:
            filters["_id"] = {"$ne": ObjectId(exclude_id)}
        return self.exists(filters)

    def code_exists(self, code: str, exclude_id: str | None = None) -> bool:
        """
        Check whether a department code already exists.
        """
        filters = {"code": code.strip().upper()}
        if exclude_id:
            filters["_id"] = {"$ne": ObjectId(exclude_id)}
        return self.exists(filters)

    def get_by_code(self, code: str):
        """
        Get a department by its code.
        """
        return self.get_one({"code": code.strip().upper()})
