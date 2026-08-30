"""
Employee Code Manager.
Generates employee codes.
"""
from __future__ import annotations
import random


class EmployeeCodeManager:
    """Employee code generation."""

    def generate(self):
        """Generate a unique employee code (e.g. EMP-4821)."""
        return f"EMP-{random.randint(1000, 9999)}"