"""
Centralized MongoDB collection names.

Every repository should use these constants instead of
hardcoding collection names.

Note: Employees are stored in the USERS collection.
"""


class Collections:
    """MongoDB collection names."""

    # ==========================
    # Authentication
    # ==========================
    USERS = "users"
    ROLES = "roles"
    PERMISSIONS = "permissions"
    TOKENS = "tokens"
    OTPS = "otps"

    # ==========================
    # Organization
    # ==========================
    DEPARTMENTS = "departments"
    DESIGNATIONS = "designations"

    # ==========================
    # Attendance & Leave
    # ==========================
    ATTENDANCE = "attendance"
    LEAVES = "leaves"

    # ==========================
    # Payment
    # ==========================
    PAYMENTS = "payments"
    AMENITIES = "amenities"

    # ==========================
    # Logs
    # ==========================
    ACTIVITY_LOGS = "activity_logs"
