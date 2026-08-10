"""
Department DTO.

Represents department data passed to the service layer.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DepartmentDTO:
    name: str
    code: str
    description: str | None = None
    head_user_id: str | None = None
    organization_id: str | None = None
    created_by: str | None = None


@dataclass
class DepartmentUpdateDTO:
    name: str | None = None
    code: str | None = None
    description: str | None = None
    head_user_id: str | None = None
    organization_id: str | None = None
    updated_by: str | None = None
