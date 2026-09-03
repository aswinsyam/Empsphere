from __future__ import annotations

import re
from datetime import datetime
from bson import ObjectId

from apps.activity_logs.services import log_activity
from apps.common.database import get_collection
from apps.common.constants import Collections
from apps.common.permissions import MANAGEABLE_ROLES, can_manage_user
from apps.common.utils import hash_password, generate_employee_code
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError


class EmployeeService:
    """Employee business logic and orchestration."""

    EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    VALID_ROLES = {"SUPER_ADMIN", "ADMIN", "HR_MANAGER", "EMPLOYEE"}
    VALID_STATUSES = {"ACTIVE", "INACTIVE"}

    def __init__(self):
        self.collection = get_collection(Collections.USERS)

    def create_employee(self, data):
        """Create a new employee after validating input."""
        first_name = data.get("first_name", "").strip()
        last_name = data.get("last_name", "").strip()
        email = (data.get("email") or "").strip().lower()
        password = data.get("password")
        role = data.get("role", "EMPLOYEE")
        phone = data.get("phone")
        status = data.get("status", "ACTIVE")

        if not first_name:
            raise ValidationError("First name is required.")
        if not last_name:
            raise ValidationError("Last name is required.")
        if not email:
            raise ValidationError("Email is required.")
        if not self.EMAIL_PATTERN.match(email):
            raise ValidationError("Enter a valid email address.")
        if not password or not str(password).strip():
            raise ValidationError("Password is required.")
        if len(str(password)) < 8:
            raise ValidationError("Password must be at least 8 characters.")
        if role and role not in self.VALID_ROLES:
            raise ValidationError(
                f"Invalid role. Must be one of: {', '.join(sorted(self.VALID_ROLES))}."
            )
        if phone and not re.match(r"^[+]?[\d\s\-()]{7,15}$", phone):
            raise ValidationError(
                "Enter a valid phone number (digits, spaces, hyphens, parentheses, and leading + allowed)."
            )
        if status and status.upper() not in self.VALID_STATUSES:
            raise ValidationError(
                f"Invalid status. Must be one of: {', '.join(self.VALID_STATUSES)}."
            )

        if self.collection.find_one({"email": email}):
            raise ValidationError("Email already exists.")

        employee_code = data.get("employee_code") or generate_employee_code()
        document = {
            "employee_code": employee_code,
            "first_name": first_name,
            "last_name": last_name,
            "full_name": f"{first_name} {last_name}".strip() or None,
            "email": email,
            "phone": (phone or "").strip(),
            "password": hash_password(password) if password else None,
            "role": role,
            "department_id": data.get("department_id"),
            "designation_id": data.get("designation_id"),
            "joining_date": str(data.get("joining_date")) if data.get("joining_date") else None,
            "status": status or "ACTIVE",
            "is_active": True,
            "login_provider": "LOCAL" if password else None,
        }
        employee_id = str(self.collection.insert_one(document).inserted_id)
        log_activity(
            module="EMPLOYEE",
            action="CREATE_EMPLOYEE",
            performed_by=str(data.get("created_by")),
            target_id=employee_id,
            status="SUCCESS",
            description=f"Created employee {first_name} {last_name} ({email}).",
        )
        return employee_id

    def get_employee(self, employee_id):
        """Get an employee."""
        if not ObjectId.is_valid(employee_id):
            raise NotFound("Employee not found.")
        employee = self.collection.find_one({"_id": ObjectId(employee_id)})
        if not employee:
            raise NotFound("Employee not found.")
        return self._serialize(employee, detail=True)

    def list_employees(self, search=None, department_id=None, status=None, page=1, page_size=10, joining_date_from=None, joining_date_to=None, actor_role=None):
        """List employees with filters and pagination.

        Backend-enforced role visibility:
            SUPER_ADMIN  -> SUPER_ADMIN, ADMIN, HR_MANAGER, EMPLOYEE
            ADMIN        -> ADMIN, HR_MANAGER, EMPLOYEE
            HR_MANAGER   -> EMPLOYEE
            EMPLOYEE     -> (should not reach here — view denies access)
        """
        query = {}
        visible_roles = self._visible_roles_for(actor_role)
        if visible_roles is None:
            query["role"] = {"$in": []}
        else:
            query["role"] = {"$in": sorted(visible_roles)}

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

        return {
            "employees": [self._serialize(e, detail=False) for e in employees],
            "total_records": total_records,
            "total_pages": total_pages,
            "page": page,
            "page_size": page_size,
        }

    def update_employee(self, employee_id, data, actor_role=None):
        """Update an employee."""
        if not ObjectId.is_valid(employee_id):
            raise NotFound("Employee not found.")
        existing = self.collection.find_one({"_id": ObjectId(employee_id)})
        if not existing:
            raise NotFound("Employee not found.")

        update_data = {}
        if data.get("first_name") not in (None, ""):
            update_data["first_name"] = data["first_name"]
        if data.get("last_name") not in (None, ""):
            update_data["last_name"] = data["last_name"]
        if data.get("email") not in (None, ""):
            update_data["email"] = data["email"]
        if data.get("phone") is not None:
            if data.get("phone") and not re.match(r"^[+]?[\d\s\-()]{7,15}$", data["phone"]):
                raise ValidationError(
                    "Enter a valid phone number (digits, spaces, hyphens, parentheses, and leading + allowed)."
                )
            update_data["phone"] = data["phone"]
        if data.get("role") not in (None, ""):
            if data["role"] not in self.VALID_ROLES:
                raise ValidationError(
                    f"Invalid role. Must be one of: {', '.join(sorted(self.VALID_ROLES))}."
                )
            update_data["role"] = data["role"]
        if data.get("department_id") is not None:
            update_data["department_id"] = data["department_id"]
        if data.get("designation_id") is not None:
            update_data["designation_id"] = data["designation_id"]
        if data.get("joining_date") is not None:
            update_data["joining_date"] = str(data["joining_date"])
        if data.get("status") not in (None, ""):
            if data["status"].upper() not in self.VALID_STATUSES:
                raise ValidationError(
                    f"Invalid status. Must be one of: {', '.join(self.VALID_STATUSES)}."
                )
            update_data["status"] = data["status"].upper()
        if data.get("employee_code") not in (None, ""):
            update_data["employee_code"] = data["employee_code"]

        if actor_role:
            target_role = existing.get("role", "EMPLOYEE")
            if not can_manage_user(actor_role, target_role):
                raise PermissionDenied("You do not have permission to update this employee.")
        if not update_data:
            return self._serialize(existing, detail=True)

        self.collection.update_one(
            {"_id": ObjectId(employee_id)},
            {"$set": update_data},
        )
        employee = self.collection.find_one({"_id": ObjectId(employee_id)})
        log_activity(
            module="EMPLOYEE",
            action="UPDATE_EMPLOYEE",
            performed_by=str(data.get("updated_by")),
            target_id=str(employee_id),
            status="SUCCESS",
            description=f"Updated employee {employee.get('first_name')} {employee.get('last_name')}.",
        )
        return self._serialize(employee, detail=True)

    def delete_employee(self, employee_id, user_id):
        """Delete an employee."""
        if not ObjectId.is_valid(employee_id):
            raise NotFound("Employee not found.")
        existing = self.collection.find_one({"_id": ObjectId(employee_id)})
        if not existing:
            raise NotFound("Employee not found.")
        self.collection.update_one(
            {"_id": ObjectId(employee_id)},
            {"$set": {"is_active": False, "is_deleted": True, "deleted_at": datetime.utcnow(), "deleted_by": user_id}},
        )
        log_activity(
            module="EMPLOYEE",
            action="DELETE_EMPLOYEE",
            performed_by=str(user_id),
            target_id=str(employee_id),
            status="SUCCESS",
            description=f"Deleted employee {existing.get('first_name')} {existing.get('last_name')}.",
        )

    def update_employee_status(self, employee_id, status, user_id, actor_role=None):
        """Update employee status."""
        if not ObjectId.is_valid(employee_id):
            raise NotFound("Employee not found.")
        existing = self.collection.find_one({"_id": ObjectId(employee_id)})
        if not existing:
            raise NotFound("Employee not found.")
        if actor_role:
            target_role = existing.get("role", "EMPLOYEE")
            if not can_manage_user(actor_role, target_role):
                raise PermissionDenied("You do not have permission to update this employee's status.")
        if status.upper() not in self.VALID_STATUSES:
            raise ValidationError(
                f"Invalid status. Must be one of: {', '.join(self.VALID_STATUSES)}."
            )
        self.collection.update_one(
            {"_id": ObjectId(employee_id)},
            {"$set": {"status": status.upper()}},
        )
        employee = self.collection.find_one({"_id": ObjectId(employee_id)})
        action = "ACTIVATE_EMPLOYEE" if status.upper() == "ACTIVE" else "DEACTIVATE_EMPLOYEE"
        log_activity(
            module="EMPLOYEE",
            action=action,
            performed_by=str(user_id),
            target_id=str(employee_id),
            status="SUCCESS",
            description=f"Updated employee status to {status.upper()}.",
        )
        return self._serialize(employee, detail=True)

    def _serialize(self, employee, detail=False):
        """Convert a raw MongoDB document into a serialized employee dict."""
        if not employee:
            return None
        serialized = {
            "user_id": str(employee.get("_id")),
            "employee_code": employee.get("employee_code"),
            "first_name": employee.get("first_name"),
            "last_name": employee.get("last_name"),
            "full_name": employee.get("full_name"),
            "email": employee.get("email"),
            "phone": employee.get("phone"),
            "role": employee.get("role"),
            "department_id": employee.get("department_id"),
            "designation_id": employee.get("designation_id"),
            "profile_image_id": str(employee.get("profile_image_id")) if employee.get("profile_image_id") else None,
            "is_email_verified": employee.get("is_email_verified"),
            "login_provider": employee.get("login_provider"),
            "last_login": employee.get("last_login"),
            "is_active": employee.get("is_active"),
            "status": employee.get("status"),
            "joining_date": employee.get("joining_date"),
            "created_at": employee.get("created_at"),
            "updated_at": employee.get("updated_at"),
        }
        if detail:
            serialized["working_duration"] = self._calculate_working_duration(
                employee.get("joining_date")
            )
            serialized["total_working_days"] = self._calculate_total_working_days(
                employee.get("joining_date")
            )
        return serialized

    @staticmethod
    def _visible_roles_for(actor_role):
        """Return the set of role names the actor is allowed to see in the
        employee-management listing. Returns ``None`` to mean "no rows".
        """
        visible = MANAGEABLE_ROLES.get(actor_role)
        if not visible:
            return None
        return set(visible)

    @staticmethod
    def _calculate_working_duration(joining_date):
        """Calculate human-readable working duration from joining date."""
        if not joining_date:
            return None
        try:
            start = datetime.strptime(str(joining_date), "%Y-%m-%d")
            now = datetime.utcnow()
            delta = now - start
            years = delta.days // 365
            months = (delta.days % 365) // 30
            days = (delta.days % 365) % 30
            parts = []
            if years:
                parts.append(f"{years} year{'s' if years != 1 else ''}")
            if months:
                parts.append(f"{months} month{'s' if months != 1 else ''}")
            if days or not parts:
                parts.append(f"{days} day{'s' if days != 1 else ''}")
            return ", ".join(parts)
        except Exception:
            return None

    @staticmethod
    def _calculate_total_working_days(joining_date):
        """Calculate total working days from joining date."""
        if not joining_date:
            return None
        try:
            start = datetime.strptime(str(joining_date), "%Y-%m-%d")
            now = datetime.utcnow()
            return (now - start).days
        except Exception:
            return None
