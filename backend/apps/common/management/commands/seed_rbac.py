"""
Seed RBAC data: roles and a default Super Admin user.

Usage:
    python manage.py seed_rbac [--email ...] [--password ...]
"""
import os
from datetime import datetime

from django.core.management.base import BaseCommand

from apps.common.constants import Collections
from apps.common.database import mongo
from apps.common.utils import hash_password


class Command(BaseCommand):
    """Seed roles and a Super Admin user."""

    help = "Seed RBAC data (roles, super admin user)."

    def add_arguments(self, parser):
        parser.add_argument("--email", type=str, default=None)
        parser.add_argument("--password", type=str, default=None)

    def handle(self, *args, **options):
        db = mongo

        email = options["email"] or os.getenv(
            "SUPER_ADMIN_EMAIL", "admin@empsphere.com"
        )
        password = options["password"] or os.getenv(
            "SUPER_ADMIN_PASSWORD", "Admin@12345"
        )
        employee_code = os.getenv("SUPER_ADMIN_EMPLOYEE_CODE", "EMP001")

        # ---- Seed roles ----
        role_col = db["roles"]
        role_count = 0
        for name in ["EMPLOYEE", "HR_MANAGER", "ADMIN", "SUPER_ADMIN"]:
            role_col.update_one(
                {"name": name},
                {
                    "$setOnInsert": {
                        "name": name,
                        "code": role_count + 1,
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
            now = datetime.utcnow()
            user_col.insert_one(
                {
                    "employee_code": employee_code,
                    "first_name": "Super",
                    "last_name": "Admin",
                    "full_name": "Super Admin",
                    "email": email.lower(),
                    "phone": "",
                    "password": hash_password(password),
                    "role": "SUPER_ADMIN",
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
