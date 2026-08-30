"""
Amenity DTOs.
Data transfer objects for office amenities.
"""
from __future__ import annotations


class AmenityCreateDTO:
    """Amenity data transfer object used during creation."""

    def __init__(
        self,
        name: str = None,
        description: str = None,
        amount: float = None,
        created_by: str = None,
    ):
        self.name = name
        self.description = description
        self.amount = amount
        self.created_by = created_by


class AmenityUpdateDTO:
    """Amenity data transfer object used during update."""

    def __init__(
        self,
        name: str = None,
        description: str = None,
        amount: float = None,
        updated_by: str = None,
    ):
        self.name = name
        self.description = description
        self.amount = amount
        self.updated_by = updated_by
