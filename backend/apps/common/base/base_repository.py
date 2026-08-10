"""
Enterprise Base Repository.

Reusable CRUD operations for all MongoDB collections.
"""

from __future__ import annotations

from typing import Any

from bson import ObjectId
from pymongo.collection import Collection

from apps.common.database.mongo import mongo
from apps.common.utils.document_helper import DocumentHelper


class BaseRepository:
    """
    Base repository that every repository inherits.
    """

    def __init__(self, collection_name: str):
        self.collection: Collection = mongo.get_collection(collection_name)

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------

    def create(
        self,
        data: dict[str, Any],
        user_id: str | None = None,
    ) -> str:

        data.update(
            DocumentHelper.create_metadata(user_id)
        )

        result = self.collection.insert_one(data)

        return str(result.inserted_id)

    # --------------------------------------------------
    # READ
    # --------------------------------------------------

    def get_by_id(self, document_id: str):

        return self.collection.find_one({
            "_id": ObjectId(document_id),
            "is_deleted": False
        })

    def get_one(self, filters: dict):

        filters["is_deleted"] = False

        return self.collection.find_one(filters)

    def get_all(self, filters=None):

        filters = filters or {}

        filters["is_deleted"] = False

        return list(self.collection.find(filters))

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------

    def update(
        self,
        document_id: str,
        data: dict,
        user_id: str | None = None,
    ):

        data.update(
            DocumentHelper.update_metadata(user_id)
        )

        result = self.collection.update_one(
            {
                "_id": ObjectId(document_id),
                "is_deleted": False
            },
            {
                "$set": data
            }
        )

        return result.modified_count > 0

    # --------------------------------------------------
    # SOFT DELETE
    # --------------------------------------------------

    def soft_delete(
        self,
        document_id: str,
        user_id: str | None = None,
    ):

        result = self.collection.update_one(
            {
                "_id": ObjectId(document_id)
            },
            {
                "$set": DocumentHelper.delete_metadata(user_id)
            }
        )

        return result.modified_count > 0

    # --------------------------------------------------
    # ACTIVATE
    # --------------------------------------------------

    def activate(self, document_id: str):

        result = self.collection.update_one(
            {
                "_id": ObjectId(document_id)
            },
            {
                "$set": {
                    "is_active": True
                }
            }
        )

        return result.modified_count > 0

    # --------------------------------------------------
    # DEACTIVATE
    # --------------------------------------------------

    def deactivate(self, document_id: str):

        result = self.collection.update_one(
            {
                "_id": ObjectId(document_id)
            },
            {
                "$set": {
                    "is_active": False
                }
            }
        )

        return result.modified_count > 0

    # --------------------------------------------------
    # COMMON
    # --------------------------------------------------

    def exists(self, filters):

        filters["is_deleted"] = False

        return self.collection.count_documents(filters, limit=1) > 0

    def count(self, filters=None):

        filters = filters or {}

        filters["is_deleted"] = False

        return self.collection.count_documents(filters)