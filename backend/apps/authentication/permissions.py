"""
Authentication module permissions.

Exposes DRF permission classes and role helpers used by the
authentication and user-management endpoints.
"""

from rest_framework.permissions import BasePermission


class IsAuthenticatedUser(BasePermission):
    """Allows access only to authenticated users."""

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user:
            return False
        if hasattr(user, "get"):
            return bool(user.get("_id"))
        return bool(getattr(user, "is_authenticated", False))
