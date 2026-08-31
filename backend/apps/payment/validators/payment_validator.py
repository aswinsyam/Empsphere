"""
Payment Validator.
Office payment validation logic.
"""
from __future__ import annotations

from apps.common.exceptions.custom_exception import ValidationException


class PaymentValidator:
    """Payment validation logic."""

    VALID_STATUSES = {"PENDING", "PAID", "FAILED", "CANCELLED"}

    @staticmethod
    def validate_create(amenity_id: str, employee_id: str = None):
        """Validate required fields for payment creation."""
        if not amenity_id or not str(amenity_id).strip():
            raise ValidationException("Amenity is required.")

    @staticmethod
    def validate_status_transition(current_status: str, new_status: str):
        """Validate payment status transition.

        Business rules:
        - PAID payments are final and cannot be changed.
        - CANCELLED payments cannot be updated.
        - FAILED payments can only be retried (set back to PENDING).
        """
        if new_status not in PaymentValidator.VALID_STATUSES:
            raise ValidationException(
                f"Invalid status. Allowed: {', '.join(PaymentValidator.VALID_STATUSES)}"
            )
        if current_status == "PAID":
            raise ValidationException("Payment is already completed.")
        if current_status == "CANCELLED":
            raise ValidationException("Cancelled payment cannot be updated.")
        if current_status == "FAILED" and new_status != "PENDING":
            raise ValidationException("Failed payment can only be retried (PENDING).")
