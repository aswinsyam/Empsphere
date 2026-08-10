"""
Authentication module permissions.

Exposes DRF permission classes and role helpers used by the
authentication and user-management endpoints.
"""

from rest_framework.permissions import BasePermission

from apps.common.core.roles import Role
from apps.common.permissions.role_permission import RolePermission


class IsAuthenticatedUser(BasePermission):
    """Allows access only to authenticated users."""

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user:
            return False
        if hasattr(user, "get"):
            return bool(user.get("_id"))
        return bool(getattr(user, "is_authenticated", False))


class IsSuperAdmin(BasePermission):
    """Allows access only to super admins."""

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user:
            return False
        return RolePermission.get_role_enum(user.get("role")) is Role.SUPER_ADMIN
