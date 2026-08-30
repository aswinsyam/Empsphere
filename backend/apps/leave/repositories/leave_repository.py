"""
Leave Repository.
Handles leave database operations.

Why this exists:
- Encapsulates all MongoDB queries for leave records.
- The service layer calls this repository instead of talking to MongoDB directly.
- This keeps database logic out of the business logic layer.

Data flow:
Repository → MongoDB collection (leaves)
"""
from __future__ import annotations

from datetime import datetime
from bson import ObjectId

from apps.common.database.mongo import mongo
from apps.common.core.collections import Collections


class LeaveRepository:
    """Leave data access layer for MongoDB operations."""

    def __init__(self):
        self.collection = mongo.get_collection(Collections.LEAVES)

    def create(self, document, user_id):
        """Create a new leave record."""
        document["created_at"] = datetime.utcnow()
        document["updated_at"] = datetime.utcnow()
        document["created_by"] = user_id
        result = self.collection.insert_one(document)
        return str(result.inserted_id)

    def get_by_id(self, leave_id):
        """Get leave by ID."""
        return self.collection.find_one({"_id": ObjectId(leave_id)})

    def get_all(self, employee_id=None, status=None, leave_type=None, start_date=None, end_date=None, page=1, page_size=10):
        """Get all leave records with optional filters."""
        query = {}
        if employee_id:
            query["employee_id"] = employee_id
        if status:
            query["status"] = status.upper()
        if leave_type:
            query["leave_type"] = leave_type.upper()

        if start_date or end_date:
            if start_date:
                query["end_date"] = {"$gte": start_date}
            if end_date:
                query.setdefault("start_date", {})["$lte"] = end_date

        total_records = self.collection.count_documents(query)
        skip = (page - 1) * page_size
        records = list(
            self.collection.find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(page_size)
        )
        total_pages = (total_records + page_size - 1) // page_size if page_size else 1
        return records, total_records, total_pages

    def update(self, leave_id, updates, user_id):
        """Update leave."""
        updates["updated_at"] = datetime.utcnow()
        self.collection.update_one(
            {"_id": ObjectId(leave_id)}, {"$set": updates}
        )
        return self.get_by_id(leave_id)
