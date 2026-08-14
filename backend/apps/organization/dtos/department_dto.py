"""
Department DTOs.
Data transfer objects for department.
"""
from __future__ import annotations


class DepartmentDTO:
    """Department data transfer object."""

    def __init__(self, name, code, description=None, head_user_id=None,
                 organization_id=None, created_by=None):
        self.name = name
        self.code = code
        self.description = description
        self.head_user_id = head_user_id
        self.organization_id = organization_id
        self.created_by = created_by


class DepartmentUpdateDTO:
    """Department update data transfer object."""

    def __init__(self, name=None, code=None, description=None,
                 head_user_id=None, organization_id=None, updated_by=None):
        self.name = name
        self.code = code
        self.description = description
        self.head_user_id = head_user_id
        self.organization_id = organization_id
        self.updated_by = updated_by