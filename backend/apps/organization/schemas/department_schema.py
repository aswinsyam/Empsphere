"""
Department Schema Definition.

Defines the structure of department documents stored in MongoDB.
This schema is reused across the organization and employee modules.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any


class DepartmentSchema:
    """
    Department document schema.
    """

    @staticmethod
    def create_document(data: dict[str, Any]) -> dict[str, Any]:
        """
        Build a new department document.
        """

        now = datetime.utcnow()

        return {
            "name": data.get("name"),
            "code": data.get("code"),
            "description": data.get("description"),
            "head_user_id": data.get("head_user_id"),
            "organization_id": data.get("organization_id"),

            "is_active": True,
            "is_deleted": False,
            "created_at": now,
            "updated_at": now,
            "created_by": data.get("created_by"),
            "updated_by": data.get("created_by"),
            "deleted_at": None,
            "deleted_by": None,
        }
