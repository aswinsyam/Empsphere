"""
Payment Service.
Handles office payment business logic with Cashfree integration.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from apps.common.base.base_service import BaseService
from apps.common.config.settings import settings
from apps.common.exceptions.custom_exception import (
    ConflictException,
    ForbiddenException,
    NotFoundException,
    ValidationException,
)
from apps.employee.repositories.employee_repository import EmployeeRepository
from apps.payment.amenities.amenity_service import AmenityService
from apps.payment.dtos.payment_dto import PaymentCreateDTO, PaymentVerifyDTO
from apps.payment.gateways.cashfree_gateway import cashfree_gateway
from apps.payment.repositories.payment_repository import PaymentRepository
from apps.payment.validators.payment_validator import PaymentValidator


class PaymentService(BaseService):
    """Office payment business logic and orchestration."""

    def __init__(self):
        super().__init__()
        self.repository = PaymentRepository()
        self.validator = PaymentValidator()
        self.amenity_service = AmenityService()
        self.employee_repository = EmployeeRepository()

    def create_payment(self, dto: PaymentCreateDTO) -> dict:
        """
        Create a new office payment and Cashfree order.

        The amount is always retrieved from the amenity configuration,
        never trusted from the frontend.

        Returns:
            Dict with payment_id and order details for frontend.
        """
        self.validator.validate_create(dto.amenity_id, dto.employee_id)

        amenity = self.amenity_service.get_active_amenity(dto.amenity_id)
        if not amenity:
            raise NotFoundException("Amenity not found or inactive.")

        employee_id = dto.employee_id
        employee = self.employee_repository.get_by_id(employee_id)
        if not employee:
            raise NotFoundException("Employee not found.")
        if not employee.get("is_active", True):
            raise ForbiddenException("Cannot create payment for an inactive employee.")

        amount = float(amenity.get("amount"))
        if amount <= 0:
            raise ValidationException("Invalid amenity amount.")

        employee_data = self.employee_repository.get_by_id(employee_id) or {}
        customer_details = {
            "customer_id": employee_id,
            "customer_name": employee_data.get("full_name", ""),
            "customer_phone": employee_data.get("phone", ""),
        }
        if employee_data.get("email"):
            customer_details["customer_email"] = employee_data["email"]

        receipt = f"payment_{employee_id}_{int(__import__('time').time())}_{uuid.uuid4().hex[:8]}"

        backend_url = getattr(settings, "BACKEND_URL", "http://localhost:8000")
        return_url = f"{backend_url}/api/payment/callback/"
        notify_url = f"{backend_url}/api/payment/webhook/"

        existing_pending = self._find_pending_payment(employee_id, dto.amenity_id)
        if existing_pending:
            return {
                "payment_id": str(existing_pending.get("_id")),
                "order_id": existing_pending.get("gateway_order_id"),
                "payment_session_id": existing_pending.get("payment_session_id"),
                "amount": amount,
                "currency": "INR",
            }

        try:
            order = cashfree_gateway.create_order(
                amount=amount,
                currency="INR",
                receipt=receipt,
                customer_details=customer_details,
                return_url=return_url,
                notify_url=notify_url,
            )
        except Exception as e:
            raise ValidationException(f"Failed to create payment order: {str(e)}")

        order_data = order if isinstance(order, dict) else {}
        gateway_order_id = order_data.get("order_id")
        payment_session_id = order_data.get("payment_session_id")

        if not gateway_order_id:
            raise ValidationException("Cashfree did not return an order ID.")

        document = {
            "employee_id": employee_id,
            "paid_by": dto.paid_by,
            "amenity_id": dto.amenity_id,
            "amenity_name": amenity.get("name"),
            "amount": amount,
            "currency": "INR",
            "status": "PENDING",
            "gateway": "CASHFREE",
            "gateway_order_id": gateway_order_id,
            "payment_session_id": payment_session_id,
            "gateway_payment_id": None,
            "payment_date": None,
        }
        payment_id = self.repository.create(document, user_id=dto.created_by)

        self.log_activity(
            module="PAYMENT",
            action="PAYMENT_CREATED",
            performed_by=str(dto.created_by),
            target_id=str(payment_id),
            status="SUCCESS",
            description=f"Created payment: {amenity.get('name')} for employee {employee_id} (₹{amount}).",
            metadata={
                "employee_id": employee_id,
                "amenity_id": dto.amenity_id,
                "amount": amount,
                "paid_by": dto.paid_by,
                "gateway_order_id": gateway_order_id,
            },
        )

        return {
            "payment_id": payment_id,
            "order_id": gateway_order_id,
            "payment_session_id": payment_session_id,
            "amount": amount,
            "currency": "INR",
        }

    def _find_pending_payment(self, employee_id: str, amenity_id: str) -> dict | None:
        """Find an existing pending payment for the same employee and amenity."""
        return self.repository.find_pending_payment(employee_id, amenity_id)

    def get_payment(self, payment_id: str) -> dict:
        """Get a payment by ID."""
        payment = self.repository.get_by_id(payment_id)
        if not payment or payment.get("is_deleted"):
            raise NotFoundException("Payment not found.")
        return self._serialize(payment)

    def list_payments(
        self,
        employee_id: str | None = None,
        department_id: str | None = None,
        amenity_id: str | None = None,
        status: str | None = None,
        date: str | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> dict:
        """List payments with optional filters."""
        records, total_records, total_pages = self.repository.get_all(
            employee_id=employee_id,
            department_id=department_id,
            amenity_id=amenity_id,
            status=status,
            date=date,
            page=page,
            page_size=page_size,
        )
        return {
            "payments": [self._serialize(p) for p in records],
            "total_records": total_records,
            "total_pages": total_pages,
            "page": page,
            "page_size": page_size,
        }

    def verify_payment(self, payment_id: str, dto: PaymentVerifyDTO, user_id: str) -> dict:
        """
        Verify Cashfree payment status via backend API and update payment status.

        Only after successful verification should the payment become PAID.
        """
        payment = self.repository.get_by_id(payment_id)
        if not payment or payment.get("is_deleted"):
            raise NotFoundException("Payment not found.")

        if payment.get("status") == "PAID":
            raise ConflictException("Payment is already verified.")

        if payment.get("status") == "CANCELLED":
            raise ConflictException("Cannot verify a cancelled payment.")

        gateway_order_id = dto.gateway_order_id or payment.get("gateway_order_id")
        if not gateway_order_id:
            raise ValidationException("Missing order ID for payment verification.")

        try:
            order_payments = cashfree_gateway.get_order_payments(gateway_order_id)
            payments_list = order_payments if isinstance(order_payments, list) else []
        except Exception as e:
            raise ValidationException(f"Failed to fetch payment status from gateway: {str(e)}")

        cashfree_status = None
        gateway_payment_id = None
        for p in payments_list:
            cf_payment_id = p.get("cf_payment_id")
            if cf_payment_id and str(cf_payment_id) == str(dto.gateway_payment_id or ""):
                cashfree_status = p.get("payment_status")
                gateway_payment_id = cf_payment_id
                break
            if not gateway_payment_id and p.get("payment_status") in ("SUCCESS", "PAID"):
                gateway_payment_id = cf_payment_id
                cashfree_status = p.get("payment_status")

        if not cashfree_status:
            cashfree_status = "PENDING"

        mapped_status = cashfree_gateway.map_payment_status(cashfree_status)

        if mapped_status == "FAILED":
            self.repository.update(payment_id, {
                "status": "FAILED",
                "gateway_payment_id": gateway_payment_id,
                "updated_by": user_id,
            })
            self.log_activity(
                module="PAYMENT",
                action="PAYMENT_FAILED",
                performed_by=str(user_id),
                target_id=str(payment_id),
                status="FAILED",
                description=f"Payment verification failed for payment {payment_id}.",
            )
            raise ValidationException("Payment verification failed. The payment was not successful.")

        if mapped_status != "PAID":
            self.repository.update(payment_id, {
                "gateway_payment_id": gateway_payment_id,
                "updated_by": user_id,
            })
            raise ValidationException(f"Payment is not yet completed. Current status: {cashfree_status}.")

        updates = {
            "status": "PAID",
            "gateway_payment_id": gateway_payment_id,
            "payment_date": datetime.utcnow(),
            "updated_by": user_id,
        }
        self.repository.update(payment_id, updates)
        payment = self.repository.get_by_id(payment_id)

        self.log_activity(
            module="PAYMENT",
            action="PAYMENT_VERIFIED",
            performed_by=str(user_id),
            target_id=str(payment_id),
            status="SUCCESS",
            description=f"Payment verified successfully: {payment.get('amenity_name')}.",
            metadata={
                "employee_id": payment.get("employee_id"),
                "amenity_id": payment.get("amenity_id"),
                "amount": payment.get("amount"),
                "gateway_payment_id": gateway_payment_id,
            },
        )
        return self._serialize(payment)

    def cancel_payment(self, payment_id: str, user_id: str) -> dict:
        """Cancel a pending payment."""
        payment = self.repository.get_by_id(payment_id)
        if not payment or payment.get("is_deleted"):
            raise NotFoundException("Payment not found.")

        if payment.get("status") == "PAID":
            raise ConflictException("Paid payment cannot be cancelled.")
        if payment.get("status") == "CANCELLED":
            raise ConflictException("Payment is already cancelled.")

        self.repository.update(payment_id, {"status": "CANCELLED", "updated_by": user_id})
        payment = self.repository.get_by_id(payment_id)

        self.log_activity(
            module="PAYMENT",
            action="PAYMENT_CANCELLED",
            performed_by=str(user_id),
            target_id=str(payment_id),
            status="SUCCESS",
            description=f"Payment cancelled: {payment.get('amenity_name')}.",
        )
        return self._serialize(payment)

    def _serialize(self, payment: dict) -> dict:
        """Convert a raw MongoDB document into a serialized payment dict."""
        if not payment:
            return None
        return {
            "payment_id": str(payment.get("_id")),
            "employee_id": payment.get("employee_id"),
            "paid_by": payment.get("paid_by"),
            "amenity_id": payment.get("amenity_id"),
            "amenity_name": payment.get("amenity_name"),
            "amount": payment.get("amount"),
            "currency": payment.get("currency", "INR"),
            "status": payment.get("status"),
            "gateway": payment.get("gateway", "CASHFREE"),
            "gateway_order_id": payment.get("gateway_order_id"),
            "gateway_payment_id": payment.get("gateway_payment_id"),
            "payment_date": payment.get("payment_date"),
            "created_at": payment.get("created_at"),
            "updated_at": payment.get("updated_at"),
        }
