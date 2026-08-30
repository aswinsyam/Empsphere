"""
Employee Repository.
Handles employee database operations using the users collection.
"""
from __future__ import annotations

import re

from bson import ObjectId

from apps.authentication.repositories.user_repository import UserRepository
from apps.common.database.mongo import mongo
from apps.common.core.collections import Collections


class EmployeeRepository:
    """Employee data access layer for MongoDB operations."""

    def __init__(self):
        self.user_repository = UserRepository()
        self.collection = mongo.get_collection(Collections.USERS)

    def create(self, document, user_id):
        """Create a new employee record."""
        return self.user_repository.create(document, user_id=user_id)

    def get_by_id(self, employee_id):
        """
        Get employee by ID.

        Returns None for a malformed id so the service layer can raise the
        standard NotFoundException instead of surfacing a BSON error.
        """
        if not ObjectId.is_valid(employee_id):
            return None
        return self.user_repository.get_by_id(employee_id)

    def get_by_email(self, email):
        """Get employee by email."""
        return self.user_repository.get_by_email(email)

    def get_all(self, search=None, department_id=None, status=None, page=1, page_size=10, joining_date_from=None, joining_date_to=None):
        """Get all employees with optional filters and pagination."""
        query = {}
        if search:
            query["$or"] = [
                {"first_name": {"$regex": re.escape(search), "$options": "i"}},
                {"last_name": {"$regex": re.escape(search), "$options": "i"}},
                {"full_name": {"$regex": re.escape(search), "$options": "i"}},
                {"email": {"$regex": re.escape(search), "$options": "i"}},
                {"employee_code": {"$regex": re.escape(search), "$options": "i"}},
                {"phone": {"$regex": re.escape(search), "$options": "i"}},
            ]
        if department_id:
            query["department_id"] = department_id
        if status:
            query["status"] = status.upper()
        if joining_date_from:
            query["joining_date"] = {"$gte": joining_date_from}
        if joining_date_to:
            if "joining_date" not in query:
                query["joining_date"] = {}
            query["joining_date"]["$lte"] = joining_date_to

        total_records = self.collection.count_documents(query)
        skip = (page - 1) * page_size
        employees = list(self.collection.find(query).skip(skip).limit(page_size))

        total_pages = (total_records + page_size - 1) // page_size if page_size else 1

        return employees, total_records, total_pages

    def update(self, employee_id, updates, user_id):
        """Update employee."""
        return self.user_repository.update(employee_id, updates)

    def soft_delete(self, employee_id, user_id):
        """Soft delete employee."""
        return self.user_repository.soft_delete(employee_id)
