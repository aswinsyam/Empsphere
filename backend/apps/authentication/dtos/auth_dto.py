"""
Authentication DTOs.

Consolidated data transfer objects for core authentication flows:
register, login, and google-login.
"""

from __future__ import annotations

from dataclasses import dataclass


# ==========================================================
# Register
# ==========================================================

@dataclass
class RegisterDTO:
    """Represents registration data passed to the service layer."""

    first_name: str
    last_name: str
    full_name: str

    email: str
    phone: str

    password: str
    confirm_password: str | None = None

    company_secret: str | None = None
    role: str = "ADMIN"

    department_id: str | None = None
    designation_id: str | None = None

    created_by: str | None = None


# ==========================================================
# Login
# ==========================================================

@dataclass
class LoginDTO:
    """Represents login credentials."""

    email: str
    password: str


# ==========================================================
# Google Login
# ==========================================================

@dataclass
class GoogleLoginDTO:
    """Represents a Google OAuth2 login."""

    id_token: str


# ==========================================================
# Profile Update
# ==========================================================

@dataclass
class UpdateProfileDTO:
    """Represents editable profile fields for the current user."""

    user_id: str
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
