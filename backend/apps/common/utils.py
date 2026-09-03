"""
Common utility functions used across multiple apps.

These are genuinely shared helpers — password hashing is needed by auth,
employee creation, and seed commands; employee-code generation is needed
by both auth and employee creation.
"""

from __future__ import annotations

import random
import re

from bson import ObjectId
from passlib.context import CryptContext
from rest_framework.exceptions import ValidationError

from apps.common.database import get_collection
from apps.common.constants import Collections

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------------------------------------
# Password helpers
# ---------------------------------------------------------

def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    if isinstance(password, str):
        b = password.encode("utf-8")
    else:
        b = bytes(password)
    if len(b) > 72:
        raise ValidationError("Password must be at most 72 bytes when UTF-8 encoded.")
    return _pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash.

    Returns False for unrecognized hashes instead of raising, so callers
    get a clean "invalid credentials" result rather than a 500.
    """
    if not hashed_password:
        return False
    try:
        return _pwd_context.verify(plain_password, hashed_password)
    except (ValueError, TypeError):
        return False


# ---------------------------------------------------------
# Employee code
# ---------------------------------------------------------

def generate_employee_code() -> str:
    """Generate a unique employee code, e.g. EMP-4821."""
    return f"EMP-{random.randint(1000, 9999)}"


# ---------------------------------------------------------
# User lookup helpers (used by many services)
# ---------------------------------------------------------

def get_user_by_email(email: str):
    """Find a user by email (case-insensitive)."""
    return get_collection(Collections.USERS).find_one({
        "email": {"$regex": f"^{re.escape(email)}$", "$options": "i"}
    })


def get_user_by_id(user_id: str):
    """Find a user by ObjectId string."""
    return get_collection(Collections.USERS).find_one({"_id": ObjectId(user_id)})
