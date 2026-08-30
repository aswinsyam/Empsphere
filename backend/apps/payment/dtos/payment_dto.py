"""
Payment DTOs.
Data transfer objects for office payment.
"""
from __future__ import annotations


class PaymentCreateDTO:
    """Payment data transfer object used during creation."""

    def __init__(
        self,
        employee_id: str = None,
        amenity_id: str = None,
        paid_by: str = None,
        created_by: str = None,
    ):
        self.employee_id = employee_id
        self.amenity_id = amenity_id
        self.paid_by = paid_by
        self.created_by = created_by


class PaymentVerifyDTO:
    """Payment verification data transfer object."""

    def __init__(
        self,
        gateway_order_id: str = None,
        gateway_payment_id: str = None,
        payment_status: str = None,
    ):
        self.gateway_order_id = gateway_order_id
        self.gateway_payment_id = gateway_payment_id
        self.payment_status = payment_status
