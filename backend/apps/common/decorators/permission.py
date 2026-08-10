"""
Role-based permission decorator.

Restricts a view to users whose role has the required privilege.
"""

from functools import wraps

from rest_framework.exceptions import PermissionDenied

from apps.common.permissions.role_permission import RolePermission


def require_role(*allowed_roles):
    """Decorator that allows only the given roles to access the view."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(view, request, *args, **kwargs):
            user = getattr(request, "user", None)

            if user is None:
                raise PermissionDenied("Authentication required.")

            user_role = user.get("role")

            if not any(
                RolePermission.has_privilege(user_role, role)
                for role in allowed_roles
            ):
                raise PermissionDenied("You do not have permission.")

            return view_func(view, request, *args, **kwargs)

        return wrapper

    return decorator
