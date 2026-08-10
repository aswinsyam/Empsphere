"""
Document helper.

Builds metadata fields applied to every MongoDB document
(created_at, updated_at, soft-delete flags, audit fields).
"""

from __future__ import annotations

from datetime import datetime


class DocumentHelper:
    """Reusable metadata builders for repository operations."""

    @staticmethod
    def create_metadata(user_id: str | None = None) -> dict:
        """Metadata for a newly created document."""
        now = datetime.utcnow()

        return {
            "is_active": True,
            "is_deleted": False,
            "created_at": now,
            "updated_at": now,
            "created_by": user_id,
            "updated_by": user_id,
            "deleted_at": None,
            "deleted_by": None,
        }

    @staticmethod
    def update_metadata(user_id: str | None = None) -> dict:
        """Metadata for an updated document."""
        return {
            "updated_at": datetime.utcnow(),
            "updated_by": user_id,
        }

    @staticmethod
    def delete_metadata(user_id: str | None = None) -> dict:
        """Metadata for a soft-deleted document."""
        return {
            "is_active": False,
            "is_deleted": True,
            "deleted_at": datetime.utcnow(),
            "deleted_by": user_id,
        }
