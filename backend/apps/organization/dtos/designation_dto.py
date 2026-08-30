"""
Designation DTOs.
Data transfer objects for designation management.
"""
from __future__ import annotations


class DesignationDTO:
    """Designation data transfer object used during creation."""

    def __init__(
        self,
        name,
        code=None,
        description=None,
        created_by=None,
    ):
        self.name = name
        self.code = code
        self.description = description
        self.created_by = created_by


class DesignationUpdateDTO:
    """Designation data transfer object used during update."""

    def __init__(
        self,
        name=None,
        code=None,
        description=None,
        is_active=None,
        updated_by=None,
    ):
        self.name = name
        self.code = code
        self.description = description
        self.is_active = is_active
        self.updated_by = updated_by
