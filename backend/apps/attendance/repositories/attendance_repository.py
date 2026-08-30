"""
Attendance Repository.
Handles attendance database operations.

Why this exists:
- Encapsulates all MongoDB queries for attendance.
- The service layer calls this repository instead of talking to MongoDB directly.
- This keeps database logic out of the business logic layer.

Data flow:
Repository → MongoDB collection (attendance)
"""
from __future__ import annotations

from datetime import datetime
from bson import ObjectId

from apps.common.database.mongo import mongo
from apps.common.core.collections import Collections


class AttendanceRepository:
    """Attendance data access layer for MongoDB operations."""

    def __init__(self):
        self.collection = mongo.get_collection(Collections.ATTENDANCE)
        self._ensure_indexes()

    def _ensure_indexes(self):
        """Create required indexes if they do not exist."""
        existing = {index["name"] for index in self.collection.list_indexes()}
        if "employee_date_unique" not in existing:
            self.collection.create_index(
                [("employee_id", 1), ("date", 1)],
                unique=True,
                name="employee_date_unique",
            )

    def create(self, document, user_id):
        """Create a new attendance record."""
        document["created_at"] = datetime.utcnow()
        document["updated_at"] = datetime.utcnow()
        document["created_by"] = user_id
        result = self.collection.insert_one(document)
        return str(result.inserted_id)

    def get_by_id(self, attendance_id):
        """Get attendance by ID."""
        return self.collection.find_one({"_id": ObjectId(attendance_id)})

    def get_by_employee_and_date(self, employee_id, date):
        """Get attendance by employee and date."""
        return self.collection.find_one({
            "employee_id": employee_id,
            "date": date,
        })

    def get_all(self, employee_id=None, start_date=None, end_date=None, status=None, page=1, page_size=20):
        """Get all attendance records with optional filters."""
        query = {}
        if employee_id:
            query["employee_id"] = employee_id
        if status:
            query["status"] = status.upper()
        if start_date:
            query["date"] = {"$gte": start_date}
        if end_date:
            query.setdefault("date", {})["$lte"] = end_date

        total_records = self.collection.count_documents(query)
        skip = (page - 1) * page_size
        records = list(
            self.collection.find(query)
            .sort("date", -1)
            .skip(skip)
            .limit(page_size)
        )
        total_pages = (total_records + page_size - 1) // page_size if page_size else 1
        return records, total_records, total_pages

    def update(self, attendance_id, updates, user_id):
        """Update attendance."""
        updates["updated_at"] = datetime.utcnow()
        self.collection.update_one(
            {"_id": ObjectId(attendance_id)}, {"$set": updates}
        )
        return self.get_by_id(attendance_id)
