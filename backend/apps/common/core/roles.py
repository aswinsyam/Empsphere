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

EMPLOYEE_MANAGER_ROLES = {
    Role.SUPER_ADMIN,
    Role.ADMIN,
    Role.HR_MANAGER,
}