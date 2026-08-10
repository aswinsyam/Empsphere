"""
User Management DTOs.

Consolidated data transfer objects for user administration
(creating Admin/HR Manager/Employee accounts).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CreateUserDTO:
    """Represents data passed to create a new user as an admin."""

    first_name: str
    last_name: str
    full_name: str

    email: str
    phone: str

    password: str

    role: str

    department_id: str | None = None
    designation_id: str | None = None

    created_by: str | None = None
