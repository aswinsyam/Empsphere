"""
User Schema Definition.

Defines the structure of user documents stored in MongoDB.
This schema is reused across authentication, user management,
and employee management modules.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any


class UserSchema:
    """
    User document schema.
    """

    @staticmethod
    def create_document(data: dict[str, Any]) -> dict[str, Any]:
        """
        Build a new user document.
        """

        now = datetime.utcnow()

        return {
            "employee_code": data.get("employee_code"),

            "first_name": data.get("first_name"),

            "last_name": data.get("last_name"),

            "full_name": data.get("full_name"),

            "email": data.get("email").lower(),

            "phone": data.get("phone"),

            "password": data.get("password"),

            "role": data.get("role"),

            "department_id": data.get("department_id"),

            "designation_id": data.get("designation_id"),

            "profile_image": "",

            "login_provider": "LOCAL",

            "google_id": None,

            "is_email_verified": False,

            "last_login": None,

            "is_active": True,

            "is_deleted": False,

            "created_at": now,

            "updated_at": now,

            "created_by": data.get("created_by"),

            "updated_by": data.get("created_by"),

            "deleted_at": None,

            "deleted_by": None,
        }
    