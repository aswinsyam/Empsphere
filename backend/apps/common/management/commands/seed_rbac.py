"""
Seed RBAC data: roles, permissions, and a default Super Admin user.

Usage:
    python manage.py seed_rbac [--email ...] [--password ...]
"""

import os

from django.core.management.base import BaseCommand

from apps.common.core.collections import Collections
from apps.common.core.roles import Role, ROLE_NAMES
from apps.common.core.permissions import (
    PERM_LOGIN,
    PERM_LOGOUT,
    PERM_PROFILE,
    PERM_USER_CREATE,
    PERM_USER_READ,
    PERM_USER_UPDATE,
    PERM_USER_DELETE,
    PERM_ROLE_CREATE,
    PERM_ROLE_READ,
    PERM_ROLE_UPDATE,
    PERM_ROLE_DELETE,
    PERM_DEPARTMENT_CREATE,
    PERM_DEPARTMENT_READ,
    PERM_DEPARTMENT_UPDATE,
    PERM_DEPARTMENT_DELETE,
    PERM_EMPLOYEE_CREATE,
    PERM_EMPLOYEE_READ,
    PERM_EMPLOYEE_UPDATE,
    PERM_EMPLOYEE_DELETE,
    PERM_ATTENDANCE_READ,
    PERM_ATTENDANCE_MARK,
    PERM_ATTENDANCE_UPDATE,
    PERM_LEAVE_CREATE,
    PERM_LEAVE_APPROVE,
    PERM_LEAVE_READ,
    PERM_PAYMENT_CREATE,
    PERM_PAYMENT_READ,
    PERM_PAYMENT_VERIFY,
    PERM_REPORT_VIEW,
    PERM_REPORT_EXPORT,
    PERM_NOTIFICATION_SEND,
)
from apps.common.database.mongo import mongo
from apps.common.security.password_manager import PasswordManager

ALL_PERMISSIONS = [
    PERM_LOGIN,
    PERM_LOGOUT,
    PERM_PROFILE,
    PERM_USER_CREATE,
    PERM_USER_READ,
    PERM_USER_UPDATE,
    PERM_USER_DELETE,
    PERM_ROLE_CREATE,
    PERM_ROLE_READ,
    PERM_ROLE_UPDATE,
    PERM_ROLE_DELETE,
    PERM_DEPARTMENT_CREATE,
    PERM_DEPARTMENT_READ,
    PERM_DEPARTMENT_UPDATE,
    PERM_DEPARTMENT_DELETE,
    PERM_EMPLOYEE_CREATE,
    PERM_EMPLOYEE_READ,
    PERM_EMPLOYEE_UPDATE,
    PERM_EMPLOYEE_DELETE,
    PERM_ATTENDANCE_READ,
    PERM_ATTENDANCE_MARK,
    PERM_ATTENDANCE_UPDATE,
    PERM_LEAVE_CREATE,
    PERM_LEAVE_APPROVE,
    PERM_LEAVE_READ,
    PERM_PAYMENT_CREATE,
    PERM_PAYMENT_READ,
    PERM_PAYMENT_VERIFY,
    PERM_REPORT_VIEW,
    PERM_REPORT_EXPORT,
    PERM_NOTIFICATION_SEND,
]


class Command(BaseCommand):
    """Seed roles, permissions and a Super Admin user."""

    help = "Seed RBAC data (roles, permissions, super admin user)."

    def add_arguments(self, parser):
        parser.add_argument("--email", type=str, default=None)
        parser.add_argument("--password", type=str, default=None)

    def handle(self, *args, **options):
        db = mongo.database

        email = options["email"] or os.getenv(
            "SUPER_ADMIN_EMAIL", "admin@empsphere.com"
        )
        password = options["password"] or os.getenv(
            "SUPER_ADMIN_PASSWORD", "Admin@12345"
        )
        employee_code = os.getenv("SUPER_ADMIN_EMPLOYEE_CODE", "EMP001")

        # ---- Seed permissions ----
        perm_col = db[Collections.PERMISSIONS]
        perm_count = 0
        for permission in ALL_PERMISSIONS:
            perm_col.update_one(
                {"key": permission},
                {
                    "$setOnInsert": {
                        "key": permission,
                        "name": permission,
                        "is_active": True,
                        "is_deleted": False,
                    }
                },
                upsert=True,
            )
            perm_count += 1
        self.stdout.write(self.style.SUCCESS("Seeded %d permissions." % perm_count))

        # ---- Seed roles ----
        role_col = db[Collections.ROLES]
        role_count = 0
        for role in Role:
            name = ROLE_NAMES[role]
            role_col.update_one(
                {"name": name},
                {
                    "$setOnInsert": {
                        "name": name,
                        "code": role.value,
                        "description": "%s role" % name,
                        "is_active": True,
                        "is_deleted": False,
                    }
                },
                upsert=True,
            )
            role_count += 1
        self.stdout.write(self.style.SUCCESS("Seeded %d roles." % role_count))

        # ---- Seed Super Admin user ----
        user_col = db[Collections.USERS]
        existing = user_col.find_one({"email": email.lower()})
        if existing:
            self.stdout.write(
                self.style.WARNING(
                    "Super Admin with email %s already exists." % email
                )
            )
        else:
            from datetime import datetime

            now = datetime.utcnow()
            user_col.insert_one(
                {
                    "employee_code": employee_code,
                    "first_name": "Super",
                    "last_name": "Admin",
                    "full_name": "Super Admin",
                    "email": email.lower(),
                    "phone": "",
                    "password": PasswordManager.hash_password(password),
                    "role": ROLE_NAMES[Role.SUPER_ADMIN],
                    "department_id": None,
                    "designation_id": None,
                    "profile_image": "",
                    "login_provider": "LOCAL",
                    "google_id": None,
                    "is_email_verified": True,
                    "last_login": None,
                    "is_active": True,
                    "is_deleted": False,
                    "created_at": now,
                    "updated_at": now,
                    "created_by": None,
                    "updated_by": None,
                    "deleted_at": None,
                    "deleted_by": None,
                }
            )
            self.stdout.write(
                self.style.SUCCESS(
                    "Created Super Admin user: %s (code: %s)"
                    % (email, employee_code)
                )
            )

        self.stdout.write(self.style.SUCCESS("RBAC seed completed."))
