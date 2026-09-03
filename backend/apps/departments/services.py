"""
Department service.
Handles department business logic.
"""
from __future__ import annotations

import re
from datetime import datetime
from bson import ObjectId

from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from apps.activity_logs.services import log_activity
from apps.common.constants import Collections
from apps.common.database import get_collection


class DepartmentService:
    """Department business logic and orchestration."""

    def __init__(self):
        self.collection = get_collection(Collections.DEPARTMENTS)
        self._ensure_indexes()

    def _ensure_indexes(self):
        """Create required indexes if they do not exist."""
        existing = {index["name"] for index in self.collection.list_indexes()}
        if "department_name_unique" not in existing:
            self.collection.create_index(
                [("name", 1)],
                unique=True,
                name="department_name_unique",
            )
        if "department_code_unique" not in existing:
            self.collection.create_index(
                [("code", 1)],
                unique=True,
                name="department_code_unique",
            )

    def create_department(self, data):
        """Create a new department after validating input."""
        name = data.get("name", "").strip()
        code = data.get("code", "").strip()
        description = data.get("description")
        head_user_id = data.get("head_user_id")
        organization_id = data.get("organization_id")
        created_by = data.get("created_by")

        if not name:
            raise ValidationError("Department name is required.")
        if not code:
            raise ValidationError("Department code is required.")

        if self.collection.find_one({"name": {"$regex": f"^{re.escape(name)}$", "$options": "i"}}):
            raise ValidationError("Department name already exists.")
        if self.collection.find_one({"code": {"$regex": f"^{re.escape(code)}$", "$options": "i"}}):
            raise ValidationError("Department code already exists.")

        document = {
            "name": name,
            "code": code,
            "description": description,
            "head_user_id": head_user_id,
            "organization_id": organization_id,
            "is_active": True,
        }
        department_id = str(self.collection.insert_one(document).inserted_id)
        log_activity(
            "DEPARTMENT", "CREATE_DEPARTMENT",
            str(created_by), department_id,
            "SUCCESS", f"Created department {name} ({code}).",
        )
        return department_id

    def get_department(self, department_id):
        """Get a department (active only — soft-deleted depts are hidden)."""
        if not ObjectId.is_valid(department_id):
            raise NotFound("Department not found.")
        department = self.collection.find_one({"_id": ObjectId(department_id)})
        if not department or not department.get("is_active"):
            raise NotFound("Department not found.")
        return self._serialize(department)

    def list_departments(self, search=None, page=1, page_size=10, include_inactive=False):
        """List departments with optional search and pagination."""
        query = {}
        if not include_inactive:
            query["is_active"] = True
        if search:
            query["$or"] = [
                {"name": {"$regex": re.escape(search), "$options": "i"}},
                {"code": {"$regex": re.escape(search), "$options": "i"}},
            ]
        total_records = self.collection.count_documents(query)
        skip = (page - 1) * page_size
        departments = list(self.collection.find(query).skip(skip).limit(page_size))
        total_pages = (total_records + page_size - 1) // page_size if page_size else 1
        return {
            "departments": [self._serialize(d) for d in departments],
            "total_records": total_records,
            "total_pages": total_pages,
            "page": page,
            "page_size": page_size,
        }

    def update_department(self, department_id, data, actor_role=None):
        """Update a department."""
        if not ObjectId.is_valid(department_id):
            raise NotFound("Department not found.")
        existing = self.collection.find_one({"_id": ObjectId(department_id)})
        if not existing:
            raise NotFound("Department not found.")

        updates = {}
        if data.get("name") not in (None, ""):
            existing_name = self.collection.find_one({"name": {"$regex": f"^{re.escape(data['name'])}$", "$options": "i"}})
            if existing_name and str(existing_name.get("_id")) != department_id:
                raise ValidationError("Department name already exists.")
            updates["name"] = data["name"]
        if data.get("code") not in (None, ""):
            existing_code = self.collection.find_one({"code": {"$regex": f"^{re.escape(data['code'])}$", "$options": "i"}})
            if existing_code and str(existing_code.get("_id")) != department_id:
                raise ValidationError("Department code already exists.")
            updates["code"] = data["code"]
        if data.get("description") is not None:
            updates["description"] = data["description"]
        if data.get("head_user_id") is not None:
            updates["head_user_id"] = data["head_user_id"]
        if data.get("organization_id") is not None:
            updates["organization_id"] = data["organization_id"]
        if data.get("is_active") is not None:
            updates["is_active"] = data["is_active"]
        if not updates:
            return self._serialize(existing)

        if data.get("name") and not str(data["name"]).strip():
            raise ValidationError("Department name cannot be empty.")

        updates["updated_at"] = datetime.utcnow()
        self.collection.update_one({"_id": ObjectId(department_id)}, {"$set": updates})
        department = self.collection.find_one({"_id": ObjectId(department_id)})
        log_activity(
            "DEPARTMENT", "UPDATE_DEPARTMENT",
            str(data.get("updated_by")), str(department_id),
            "SUCCESS", f"Updated department {department.get('name')} ({department.get('code')}).",
        )
        return self._serialize(department)

    def delete_department(self, department_id, user_id, actor_role=None):
        """Delete a department."""
        if not ObjectId.is_valid(department_id):
            raise NotFound("Department not found.")
        existing = self.collection.find_one({"_id": ObjectId(department_id)})
        if not existing:
            raise NotFound("Department not found.")
        users_collection = get_collection(Collections.USERS)
        employee_count = users_collection.count_documents({"department_id": department_id})
        if employee_count > 0:
            raise PermissionDenied(
                "Cannot delete department because employees are assigned to it."
            )
        self.collection.update_one(
            {"_id": ObjectId(department_id)},
            {"$set": {"is_active": False}},
        )
        log_activity(
            "DEPARTMENT", "DELETE_DEPARTMENT",
            str(user_id), str(department_id),
            "SUCCESS", f"Deleted department {existing.get('name')} ({existing.get('code')}).",
        )

    def _serialize(self, department):
        """Convert a raw MongoDB document into a serialized department dict."""
        if not department:
            return None
        users_collection = get_collection(Collections.USERS)
        return {
            "department_id": str(department.get("_id")),
            "name": department.get("name"),
            "code": department.get("code"),
            "description": department.get("description"),
            "head_user_id": department.get("head_user_id"),
            "organization_id": department.get("organization_id"),
            "is_active": department.get("is_active"),
            "employee_count": users_collection.count_documents({"department_id": str(department.get("_id"))}),
            "created_at": department.get("created_at"),
            "updated_at": department.get("updated_at"),
        }
