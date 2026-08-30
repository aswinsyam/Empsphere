"""
Department DTOs.
Data transfer objects for department.
"""
from __future__ import annotations


class DepartmentDTO:
    """Department data transfer object used during creation."""

    def __init__(self, name, code, description=None, head_user_id=None,
                 organization_id=None, created_by=None):
        self.name = name
        self.code = code
        self.description = description
        self.head_user_id = head_user_id
        self.organization_id = organization_id
        self.created_by = created_by


class DepartmentUpdateDTO:
    """Department data transfer object used during update."""

    def __init__(self, name=None, code=None, description=None,
                 head_user_id=None, organization_id=None, is_active=None, updated_by=None):
        self.name = name
        self.code = code
        self.description = description
        self.head_user_id = head_user_id
        self.organization_id = organization_id
        self.is_active = is_active
        self.updated_by = updated_by