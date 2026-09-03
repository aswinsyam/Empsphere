"""
Shared constants: collection names, OTP policy, password rules, roles.
"""

import re
from enum import IntEnum


# =========================================================
# MongoDB collection names
# =========================================================

class Collections:
    """MongoDB collection names."""

    USERS = "users"
    ROLES = "roles"
    PERMISSIONS = "permissions"
    TOKENS = "tokens"
    OTPS = "otps"

    DEPARTMENTS = "departments"
    DESIGNATIONS = "designations"

    ATTENDANCE = "attendance"
    LEAVES = "leaves"

    PAYMENTS = "payments"
    AMENITIES = "amenities"

    ACTIVITY_LOGS = "activity_logs"


# =========================================================
# OTP policy
# =========================================================

class OTPPurpose:
    """Supported OTP purposes."""

    EMAIL_VERIFICATION = "email_verification"
    FIRST_LOGIN = "first_login"
    PASSWORD_SETUP = "password_setup"
    FORGOT_PASSWORD = "forgot_password"

    ALL = (
        EMAIL_VERIFICATION,
        FIRST_LOGIN,
        PASSWORD_SETUP,
        FORGOT_PASSWORD,
    )

    DEFAULT = EMAIL_VERIFICATION


OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 10


# =========================================================
# Password policy (mirrored by frontend helpers.ts)
# =========================================================

PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$")
PASSWORD_RULE_MESSAGE = (
    "Password must be at least 8 characters and include an uppercase letter, "
    "a lowercase letter, and a number."
)


# =========================================================
# Roles
# =========================================================

class Role(IntEnum):
    """System roles ordered by privilege."""

    EMPLOYEE = 1
    HR_MANAGER = 2
    ADMIN = 3
    SUPER_ADMIN = 4


ROLE_NAMES = {
    Role.EMPLOYEE: "EMPLOYEE",
    Role.HR_MANAGER: "HR_MANAGER",
    Role.ADMIN: "ADMIN",
    Role.SUPER_ADMIN: "SUPER_ADMIN",
}
