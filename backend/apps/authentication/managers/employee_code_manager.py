"""
Employee Code Manager.
Generates employee codes.
"""
from __future__ import annotations
import random


class EmployeeCodeManager:
    """Employee code generation."""

    def generate(self):
        """Generate employee code."""
        return f"EMP-{random.randint(1000, 9999)}"