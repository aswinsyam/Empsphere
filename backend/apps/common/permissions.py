"""
Shared authentication and permission helpers.

Three layers of auth are kept deliberately separate:

1. **Authentication** — who is this user?  (JWTAuthentication in this package's
   authentication module — it decodes the token and loads the user document.)

2. **Permission** — does this user have the right role?  (IsAuthenticatedUser
   default permission + the ``require_role`` decorator used on individual views.)

3. **Ownership** — can this user manage this specific resource?  (can_manage_user
   used in services for business-logic checks, e.g. an HR_MANAGER can edit an
   EMPLOYEE but not an ADMIN.)
"""

from functools import wraps

from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied


class IsAuthenticatedUser(BasePermission):
    """Default permission — allows access only to authenticated users."""

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user:
            return False
        if hasattr(user, "get"):
            return bool(user.get("_id"))
        return bool(getattr(user, "is_authenticated", False))


def require_role(*allowed_roles):
    """View-method decorator — allow only the given roles.

    Example::

        @require_role("SUPER_ADMIN", "ADMIN", "HR_MANAGER")
        def post(self, request):
            ...
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(view, request, *args, **kwargs):
            user = getattr(request, "user", None)
            if user is None:
                raise PermissionDenied("Authentication required.")
            user_role = user.get("role")
            if user_role not in allowed_roles:
                raise PermissionDenied("You do not have permission.")
            return view_func(view, request, *args, **kwargs)

        return wrapper

    return decorator


# Which roles a role may manage. Lower-privilege roles manage fewer targets.
MANAGEABLE_ROLES = {
    "SUPER_ADMIN": {"SUPER_ADMIN", "ADMIN", "HR_MANAGER", "EMPLOYEE"},
    "ADMIN": {"HR_MANAGER", "EMPLOYEE"},
    "HR_MANAGER": {"EMPLOYEE"},
    "EMPLOYEE": set(),
}


def can_manage_user(actor_role, target_role):
    """Return True if *actor_role* may manage a user with *target_role*."""
    return target_role in MANAGEABLE_ROLES.get(actor_role, set())
