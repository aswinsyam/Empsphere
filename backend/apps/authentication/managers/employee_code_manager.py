"""
Employee Code Manager.

Generates unique employee codes.
"""

from apps.authentication.repositories.sequence_repository import (
    SequenceRepository,
)


class EmployeeCodeManager:

    def __init__(self):
        self.sequence_repository = SequenceRepository()

    def generate(self) -> str:
        """
        Generate a unique employee code.
        """

        sequence = self.sequence_repository.get_next_sequence(
            "employee_code"
        )

        return f"EMP{sequence:06d}"
    