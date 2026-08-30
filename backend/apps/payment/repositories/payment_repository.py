"""
Payment Repository.
Handles office payment database operations.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from bson import ObjectId

from apps.common.database.mongo import mongo
from apps.common.core.collections import Collections


class PaymentRepository:
    """Payment data access layer for MongoDB operations."""

    def __init__(self):
        self.collection = mongo.get_collection(Collections.PAYMENTS)
        self.users_collection = mongo.get_collection(Collections.USERS)
        self._ensure_indexes()

    def _ensure_indexes(self):
        """Create required indexes if they do not exist."""
        existing = {index["name"] for index in self.collection.list_indexes()}
        if "employee_status_idx" not in existing:
            self.collection.create_index(
                [("employee_id", 1), ("status", 1)],
                name="employee_status_idx",
            )
        if "created_at_idx" not in existing:
            self.collection.create_index(
                [("created_at", -1)],
                name="created_at_idx",
            )
        if "amenity_idx" not in existing:
            self.collection.create_index(
                [("amenity_id", 1)],
                name="amenity_idx",
            )
        if "department_idx" not in existing:
            self.collection.create_index(
                [("department_id", 1)],
                name="department_idx",
            )
        if "gateway_order_id_unique" not in existing:
            self.collection.create_index(
                [("gateway_order_id", 1)],
                unique=True,
                sparse=True,
                name="gateway_order_id_unique",
            )
        if "gateway_payment_id_unique" not in existing:
            self.collection.create_index(
                [("gateway_payment_id", 1)],
                unique=True,
                sparse=True,
                name="gateway_payment_id_unique",
            )

    def create(self, document: dict[str, Any], user_id: str) -> str:
        """Create a new payment record."""
        document["created_at"] = datetime.utcnow()
        document["updated_at"] = datetime.utcnow()
        document["created_by"] = user_id
        result = self.collection.insert_one(document)
        return str(result.inserted_id)

    def get_by_id(self, payment_id: str) -> dict[str, Any] | None:
        """Get payment by ID."""
        if not ObjectId.is_valid(payment_id):
            return None
        return self.collection.find_one({"_id": ObjectId(payment_id)})

    def get_by_order_id(self, order_id: str) -> dict[str, Any] | None:
        """Get payment by gateway order ID."""
        return self.collection.find_one({"gateway_order_id": order_id})

    def find_pending_payment(self, employee_id: str, amenity_id: str) -> dict[str, Any] | None:
        """Find an existing pending payment for the same employee and amenity (idempotency)."""
        return self.collection.find_one({
            "employee_id": employee_id,
            "amenity_id": amenity_id,
            "status": "PENDING",
            "is_deleted": {"$ne": True},
        })

    def get_all(
        self,
        employee_id: str | None = None,
        department_id: str | None = None,
        amenity_id: str | None = None,
        status: str | None = None,
        date: str | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[dict[str, Any]], int, int]:
        """Get all payment records with optional filters."""
        query: dict[str, Any] = {"is_deleted": {"$ne": True}}

        if employee_id:
            query["employee_id"] = employee_id

        if department_id:
            employee_ids = self._get_employee_ids_by_department(department_id)
            query["employee_id"] = {"$in": employee_ids}

        if amenity_id:
            query["amenity_id"] = amenity_id

        if status:
            query["status"] = status.upper()

        if date:
            try:
                filter_date = datetime.strptime(date, "%Y-%m-%d")
                next_date = filter_date + timedelta(days=1)
                query["created_at"] = {"$gte": filter_date, "$lt": next_date}
            except ValueError:
                pass

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

    def _get_employee_ids_by_department(self, department_id: str) -> list[str]:
        """Get all employee IDs in a department."""
        employees = self.users_collection.find(
            {"department_id": department_id, "is_deleted": {"$ne": True}},
            {"_id": 1},
        )
        return [str(e["_id"]) for e in employees]

    def update(self, payment_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
        """Update payment."""
        updates["updated_at"] = datetime.utcnow()
        self.collection.update_one(
            {"_id": ObjectId(payment_id)}, {"$set": updates}
        )
        return self.get_by_id(payment_id)

    def soft_delete(self, payment_id: str, user_id: str):
        """Soft delete payment."""
        self.collection.update_one(
            {"_id": ObjectId(payment_id)},
            {"$set": {"is_deleted": True, "deleted_at": datetime.utcnow(), "deleted_by": user_id}},
        )
