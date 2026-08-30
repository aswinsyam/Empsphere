"""
Role definitions and role hierarchy.

This module provides a centralized place for all system roles
used throughout the application.
"""

from enum import IntEnum


class Role(IntEnum):
    """System roles ordered by privilege."""

    EMPLOYEE = 1
    HR_MANAGER = 2
    ADMIN = 3
    SUPER_ADMIN = 4


# =====================================================
# Database Role Names
# =====================================================

ROLE_NAMES = {
    Role.EMPLOYEE: "EMPLOYEE",
    Role.HR_MANAGER: "HR_MANAGER",
    Role.ADMIN: "ADMIN",
    Role.SUPER_ADMIN: "SUPER_ADMIN",
}

ROLE_LOOKUP = {value: key for key, value in ROLE_NAMES.items()}


# =====================================================
# Role Groups
# =====================================================

MANAGEMENT_ROLES = {
    Role.SUPER_ADMIN,
    Role.ADMIN,
    Role.HR_MANAGER,
}

HIGH_PRIVILEGE_ROLES = {
    Role.SUPER_ADMIN,
    Role.ADMIN,
}

EMPLOYEE_MANAGER_ROLES = {
    Role.SUPER_ADMIN,
    Role.ADMIN,
    Role.HR_MANAGER,
}


# =====================================================
# Helper Functions
# =====================================================

def has_role(required_role: Role, current_role: Role) -> bool:
    """
    Check whether the current role has enough privilege.

    Example:
        has_role(Role.ADMIN, Role.SUPER_ADMIN) -> True
        has_role(Role.ADMIN, Role.HR_MANAGER) -> False
    """
    return current_role >= required_role


def is_super_admin(role: Role) -> bool:
    """Return True if the role is SUPER_ADMIN."""
    return role == Role.SUPER_ADMIN


def is_admin(role: Role) -> bool:
    """Return True if the role is ADMIN."""
    return role == Role.ADMIN


def is_hr(role: Role) -> bool:
    """Return True if the role is HR_MANAGER."""
    return role == Role.HR_MANAGER


def is_employee(role: Role) -> bool:
    """Return True if the role is EMPLOYEE."""
    return role == Role.EMPLOYEE