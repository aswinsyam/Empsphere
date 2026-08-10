"""
Permission definitions for Role-Based Access Control (RBAC).

Every protected API should reference these permission constants
instead of hardcoding permission strings.
"""

from apps.common.core.roles import Role


# ==========================================================
# Authentication
# ==========================================================

PERM_LOGIN = "auth.login"
PERM_LOGOUT = "auth.logout"
PERM_PROFILE = "auth.profile"


# ==========================================================
# User Management
# ==========================================================

PERM_USER_CREATE = "user.create"
PERM_USER_READ = "user.read"
PERM_USER_UPDATE = "user.update"
PERM_USER_DELETE = "user.delete"


# ==========================================================
# Role Management
# ==========================================================

PERM_ROLE_CREATE = "role.create"
PERM_ROLE_READ = "role.read"
PERM_ROLE_UPDATE = "role.update"
PERM_ROLE_DELETE = "role.delete"


# ==========================================================
# Department Management
# ==========================================================

PERM_DEPARTMENT_CREATE = "department.create"
PERM_DEPARTMENT_READ = "department.read"
PERM_DEPARTMENT_UPDATE = "department.update"
PERM_DEPARTMENT_DELETE = "department.delete"


# ==========================================================
# Employee Management
# ==========================================================

PERM_EMPLOYEE_CREATE = "employee.create"
PERM_EMPLOYEE_READ = "employee.read"
PERM_EMPLOYEE_UPDATE = "employee.update"
PERM_EMPLOYEE_DELETE = "employee.delete"


# ==========================================================
# Attendance
# ==========================================================

PERM_ATTENDANCE_READ = "attendance.read"
PERM_ATTENDANCE_MARK = "attendance.mark"
PERM_ATTENDANCE_UPDATE = "attendance.update"


# ==========================================================
# Leave
# ==========================================================

PERM_LEAVE_CREATE = "leave.create"
PERM_LEAVE_APPROVE = "leave.approve"
PERM_LEAVE_READ = "leave.read"


# ==========================================================
# Payroll
# ==========================================================

PERM_PAYROLL_CREATE = "payroll.create"
PERM_PAYROLL_READ = "payroll.read"
PERM_PAYROLL_UPDATE = "payroll.update"


# ==========================================================
# Reports
# ==========================================================

PERM_REPORT_VIEW = "report.view"
PERM_REPORT_EXPORT = "report.export"


# ==========================================================
# Notification
# ==========================================================

PERM_NOTIFICATION_SEND = "notification.send"


# ==========================================================
# Permission Mapping
# ==========================================================

ROLE_PERMISSIONS = {

    # ---------------- Authentication ----------------

    PERM_LOGIN: {
        Role.SUPER_ADMIN,
        Role.ADMIN,
        Role.HR_MANAGER,
        Role.EMPLOYEE,
    },

    PERM_LOGOUT: {
        Role.SUPER_ADMIN,
        Role.ADMIN,
        Role.HR_MANAGER,
        Role.EMPLOYEE,
    },

    PERM_PROFILE: {
        Role.SUPER_ADMIN,
        Role.ADMIN,
        Role.HR_MANAGER,
        Role.EMPLOYEE,
    },

    # ---------------- User ----------------

    PERM_USER_CREATE: {
        Role.SUPER_ADMIN,
        Role.ADMIN,
    },

    PERM_USER_READ: {
        Role.SUPER_ADMIN,
        Role.ADMIN,
        Role.HR_MANAGER,
    },

    PERM_USER_UPDATE: {
        Role.SUPER_ADMIN,
        Role.ADMIN,
    },

    PERM_USER_DELETE: {
        Role.SUPER_ADMIN,
    },

    # ---------------- Role ----------------

    PERM_ROLE_CREATE: {
        Role.SUPER_ADMIN,
    },

    PERM_ROLE_READ: {
        Role.SUPER_ADMIN,
        Role.ADMIN,
    },

    PERM_ROLE_UPDATE: {
        Role.SUPER_ADMIN,
    },

    PERM_ROLE_DELETE: {
        Role.SUPER_ADMIN,
    },

    # ---------------- Department ----------------

    PERM_DEPARTMENT_CREATE: {
        Role.SUPER_ADMIN,
        Role.ADMIN,
    },

    PERM_DEPARTMENT_READ: {
        Role.SUPER_ADMIN,
        Role.ADMIN,
        Role.HR_MANAGER,
    },

    PERM_DEPARTMENT_UPDATE: {
        Role.SUPER_ADMIN,
        Role.ADMIN,
    },

    PERM_DEPARTMENT_DELETE: {
        Role.SUPER_ADMIN,
    },

    # ---------------- Employee ----------------

    PERM_EMPLOYEE_CREATE: {
        Role.SUPER_ADMIN,
        Role.ADMIN,
        Role.HR_MANAGER,
    },

    PERM_EMPLOYEE_READ: {
        Role.SUPER_ADMIN,
        Role.ADMIN,
        Role.HR_MANAGER,
    },

    PERM_EMPLOYEE_UPDATE: {
        Role.SUPER_ADMIN,
        Role.ADMIN,
        Role.HR_MANAGER,
    },

    PERM_EMPLOYEE_DELETE: {
        Role.SUPER_ADMIN,
    },

    # ---------------- Attendance ----------------

    PERM_ATTENDANCE_MARK: {
        Role.EMPLOYEE,
    },

    PERM_ATTENDANCE_READ: {
        Role.SUPER_ADMIN,
        Role.ADMIN,
        Role.HR_MANAGER,
        Role.EMPLOYEE,
    },

    PERM_ATTENDANCE_UPDATE: {
        Role.ADMIN,
        Role.HR_MANAGER,
    },

    # ---------------- Leave ----------------

    PERM_LEAVE_CREATE: {
        Role.EMPLOYEE,
    },

    PERM_LEAVE_APPROVE: {
        Role.ADMIN,
        Role.HR_MANAGER,
    },

    PERM_LEAVE_READ: {
        Role.SUPER_ADMIN,
        Role.ADMIN,
        Role.HR_MANAGER,
        Role.EMPLOYEE,
    },

    # ---------------- Payroll ----------------

    PERM_PAYROLL_CREATE: {
        Role.ADMIN,
    },

    PERM_PAYROLL_READ: {
        Role.SUPER_ADMIN,
        Role.ADMIN,
        Role.HR_MANAGER,
        Role.EMPLOYEE,
    },

    PERM_PAYROLL_UPDATE: {
        Role.ADMIN,
    },

    # ---------------- Reports ----------------

    PERM_REPORT_VIEW: {
        Role.SUPER_ADMIN,
        Role.ADMIN,
        Role.HR_MANAGER,
    },

    PERM_REPORT_EXPORT: {
        Role.SUPER_ADMIN,
        Role.ADMIN,
    },

    # ---------------- Notification ----------------

    PERM_NOTIFICATION_SEND: {
        Role.SUPER_ADMIN,
        Role.ADMIN,
        Role.HR_MANAGER,
    },
}


def roles_for_permission(permission: str) -> set:
    """
    Return the roles that have the given permission.
    """
    return ROLE_PERMISSIONS.get(permission, set())


def has_permission(role: Role, permission: str) -> bool:
    """
    Check whether a role has a specific permission.
    """
    return role in ROLE_PERMISSIONS.get(permission, set())