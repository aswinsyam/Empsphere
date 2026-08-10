"""
User management validators.

Domain-level business rules for user administration, particularly
the role-hierarchy rules that govern who can create which role.
"""

from apps.common.core.roles import ROLE_LOOKUP, Role
from apps.common.exceptions.custom_exception import (
    ForbiddenException,
    ValidationException,
)


def validate_target_role(role: str) -> str:
    """
    Validate and normalize the target role string for user creation.

    Returns the normalized uppercase role name.
    """
    role = (role or "").strip().upper()

    if role not in ROLE_LOOKUP:
        raise ValidationException(f"Invalid role: {role}")

    return role


def validate_role_privilege(
    actor_role: str,
    target_role: str,
    createable_map: dict,
) -> None:
    """
    Ensure the actor (by role) is allowed to create the target role.

    Arguments:
        actor_role: role name of the authenticated caller.
        target_role: role name to be created.
        createable_map: maps an actor Role enum to a set of allowed
            target Role enums.

    Raises:
        ForbiddenException: if the actor cannot create the target role.
        ValidationException: if the actor role is unknown.
    """
    actor_enum = ROLE_LOOKUP.get((actor_role or "").strip().upper())
    target_enum = ROLE_LOOKUP.get((target_role or "").strip().upper())

    if actor_enum is None:
        raise ValidationException("Invalid actor role.")

    if target_enum is None:
        raise ValidationException("Invalid target role.")

    allowed = createable_map.get(actor_enum, frozenset())

    if target_enum not in allowed:
        raise ForbiddenException(
            "You do not have permission to create a user with this role."
        )
