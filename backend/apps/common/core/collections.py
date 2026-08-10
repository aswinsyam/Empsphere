"""
Centralized MongoDB collection names.

Every repository should use these constants instead of
hardcoding collection names.
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
    SEQUENCES = "sequences"
    OTPS = "otps"

    # ==========================
    # Organization
    # ==========================
    ORGANIZATIONS = "organizations"
    DEPARTMENTS = "departments"
    DESIGNATIONS = "designations"

    # ==========================
    # Employee
    # ==========================
    EMPLOYEES = "employees"

    # ==========================
    # Attendance & Leave
    # ==========================
    ATTENDANCE = "attendance"
    LEAVES = "leaves"

    # ==========================
    # Payroll
    # ==========================
    PAYROLLS = "payrolls"
    PAYSLIPS = "payslips"

    # ==========================
    # Notifications
    # ==========================
    NOTIFICATIONS = "notifications"

    # ==========================
    # Reports
    # ==========================
    REPORTS = "reports"

    # ==========================
    # Logs
    # ==========================
    AUDIT_LOGS = "audit_logs"
    ACTIVITY_LOGS = "activity_logs"