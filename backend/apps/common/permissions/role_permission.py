"""
Role-based permission helper.

Determines whether a user's role is allowed to perform an action.
"""

from __future__ import annotations

from apps.common.core.roles import Role, ROLE_LOOKUP, ROLE_NAMES


class RolePermission:
    """Helpers to check role privileges."""

    @staticmethod
    def get_role_enum(role) -> Role | None:
        """Convert a role string/int into a Role enum."""
        if isinstance(role, Role):
            return role
        if isinstance(role, int):
            try:
                return Role(role)
            except ValueError:
                return None
        if isinstance(role, str):
            return ROLE_LOOKUP.get(role)
        return None

    @staticmethod
    def role_name(role: Role) -> str:
        """Return the string name for a role."""
        return ROLE_NAMES.get(role, str(role))

    @staticmethod
    def has_privilege(user_role, required_role: Role) -> bool:
        """Check if user_role is at least required_role in the hierarchy."""
        role = RolePermission.get_role_enum(user_role)
        if role is None:
            return False
        return role.value >= required_role.value

    # ----------------------------------------------------------
    # Reusable RBAC helpers
    # ----------------------------------------------------------

    # Roles that a given actor role may "manage" (create/update/etc.).
    # SUPER_ADMIN manages everyone; ADMIN manages HR + Employee; HR manages
    # Employee only; EMPLOYEE can manage nobody.
    MANAGABLE_ROLES = {
        Role.SUPER_ADMIN: {
            Role.SUPER_ADMIN,
            Role.ADMIN,
            Role.HR_MANAGER,
            Role.EMPLOYEE,
        },
        Role.ADMIN: {Role.HR_MANAGER, Role.EMPLOYEE},
        Role.HR_MANAGER: {Role.EMPLOYEE},
        Role.EMPLOYEE: set(),
    }

    @staticmethod
    def can_manage_user(actor_role, target_role) -> bool:
        """
        Return True if the actor's role may manage a user with the given role.

        A SUPER_ADMIN can manage everyone; an ADMIN can manage HR managers and
        employees; an HR manager can manage employees; an EMPLOYEE cannot
        manage anyone.
        """
        actor = RolePermission.get_role_enum(actor_role)
        target = RolePermission.get_role_enum(target_role)
        if actor is None or target is None:
            return False
        return target in RolePermission.MANAGABLE_ROLES.get(actor, set())

    @staticmethod
    def can_assign_role(actor_role, target_role) -> bool:
        """
        Return True if the actor's role may assign (create a user with) the
        given target role. This is the authorization rule used by the
        create-user endpoint.
        """
        return RolePermission.can_manage_user(actor_role, target_role)

    @staticmethod
    def can_manage_employee(actor_role) -> bool:
        """
        Return True if the actor's role may manage EMPLOYEE accounts.
        """
        return RolePermission.can_manage_user(actor_role, Role.EMPLOYEE)

    @staticmethod
    def owns_resource(actor, resource_user_id) -> bool:
        """
        Return True if the actor owns the given resource.

        Used so an EMPLOYEE can only access their own profile. Actor may be a
        user dict or a raw user id string.
        """
        actor_id = actor.get("_id") if isinstance(actor, dict) else actor
        if actor_id is None or resource_user_id is None:
            return False
        return str(actor_id) == str(resource_user_id)
