from __future__ import annotations

import json
import logging
from datetime import datetime

from django.shortcuts import redirect
from rest_framework import status
from rest_framework.views import APIView

from apps.activity_logs.services import log_activity
from apps.common.database import get_collection
from apps.common.constants import Collections
from apps.common.permissions import require_role
from apps.common.responses import success, error
from apps.common.settings import settings
from apps.payments.gateways import razorpay_gateway
from apps.payments.serializers import (
    AmenityCreateSerializer,
    AmenityUpdateSerializer,
    PaymentCreateSerializer,
    PaymentVerifySerializer,
)
from apps.payments.services import PaymentService, AmenityService

logger = logging.getLogger(__name__)


class PaymentView(APIView):
    """Office payment endpoints."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.payment_service = PaymentService()

    @require_role("SUPER_ADMIN", "ADMIN", "HR_MANAGER", "EMPLOYEE")
    def post(self, request):
        """Create a new office payment and Razorpay order."""
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_role = request.user.get("role")
        user_id = str(request.user["_id"])
        amenity_id = serializer.validated_data["amenity_id"]

        employee_id = serializer.validated_data.get("employee_id")

        if user_role == "EMPLOYEE":
            employee_id = user_id
        elif not employee_id:
            if user_role == "SUPER_ADMIN":
                return error("Employee is required.", status_code=status.HTTP_400_BAD_REQUEST)
            employee_id = user_id

        result = self.payment_service.create_payment({
            "employee_id": employee_id,
            "amenity_id": amenity_id,
            "paid_by": user_id,
            "created_by": user_id,
        })

        return success("Payment initiated.", result, status_code=status.HTTP_201_CREATED)

    @require_role("SUPER_ADMIN", "ADMIN", "HR_MANAGER", "EMPLOYEE")
    def get(self, request, payment_id=None):
        """List payments, get a single payment, or get current user's payments."""
        url_name = request.resolver_match.url_name
        if url_name == "payment-me":
            return self._get_my_payments(request)

        user_role = request.user.get("role")
        user_id = str(request.user["_id"])

        if payment_id:
            payment = self.payment_service.get_payment(payment_id)
            if user_role == "EMPLOYEE" and payment.get("employee_id") != user_id:
                return error("You do not have permission to view this payment.", status_code=status.HTTP_403_FORBIDDEN)
            return success(data=payment)

        employee_id = request.query_params.get("employee_id")
        department_id = request.query_params.get("department_id")
        amenity_id = request.query_params.get("amenity_id")
        status_filter = request.query_params.get("status")
        date = request.query_params.get("date")
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))

        if user_role == "EMPLOYEE":
            employee_id = user_id
            department_id = None
            amenity_id = None

        result = self.payment_service.list_payments(
            employee_id=employee_id,
            department_id=department_id,
            amenity_id=amenity_id,
            status=status_filter,
            date=date,
            page=page,
            page_size=page_size,
        )
        return success(data=result)

    def _get_my_payments(self, request):
        """Get current user's payments."""
        user_id = str(request.user["_id"])
        status_filter = request.query_params.get("status")
        date = request.query_params.get("date")
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))

        result = self.payment_service.list_payments(
            employee_id=user_id,
            status=status_filter,
            date=date,
            page=page,
            page_size=page_size,
        )
        return success(data=result)


class PaymentVerifyView(APIView):
    """Payment verification endpoint."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.payment_service = PaymentService()

    @require_role("SUPER_ADMIN", "ADMIN", "HR_MANAGER", "EMPLOYEE")
    def post(self, request, payment_id):
        """Verify Razorpay Checkout signature and mark the payment as PAID."""
        serializer = PaymentVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment = self.payment_service.verify_payment(
            payment_id,
            serializer.validated_data,
            user_id=str(request.user["_id"])
        )

        return success("Payment verified.", payment)


class PaymentCancelView(APIView):
    """Payment cancellation endpoint."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.payment_service = PaymentService()

    @require_role("SUPER_ADMIN", "ADMIN", "HR_MANAGER", "EMPLOYEE")
    def post(self, request, payment_id):
        """Cancel a pending payment."""
        user_role = request.user.get("role")
        user_id = str(request.user["_id"])

        payment = self.payment_service.get_payment(payment_id)

        if user_role == "EMPLOYEE" and payment.get("employee_id") != user_id:
            return error("You do not have permission to cancel this payment.", status_code=status.HTTP_403_FORBIDDEN)

        payment = self.payment_service.cancel_payment(
            payment_id, user_id=user_id
        )

        return success("Payment cancelled.", payment)


class RazorpayWebhookView(APIView):
    """
    Razorpay webhook endpoint.

    Razorpay sends webhook events to this endpoint for asynchronous payment
    status updates. We verify the ``X-Razorpay-Signature`` header against the
    raw request body using the webhook secret before processing anything.
    The handler is idempotent — re-deliveries for the same gateway payment
    id are ignored once the payment is in a terminal state.
    """

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        """Handle incoming Razorpay webhook events."""
        signature = request.headers.get("X-Razorpay-Signature")
        if not signature:
            return error("Missing signature")

        raw_body = request.body
        if isinstance(raw_body, str):
            raw_body = raw_body.encode("utf-8")

        if not razorpay_gateway.verify_webhook_signature(signature, raw_body):
            return error("Invalid signature")

        try:
            event_data = json.loads(raw_body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return error("Invalid JSON")

        event_type = event_data.get("event")
        event_payload = event_data.get("payload", {})
        payment_entity = event_payload.get("payment", {}).get("entity", {})
        order_entity = event_payload.get("order", {}).get("entity", {}) or {}

        handlers = {
            "payment.authorized": self._handle_payment_authorized,
            "payment.captured": self._handle_payment_captured,
            "payment.failed": self._handle_payment_failed,
        }

        handler = handlers.get(event_type)
        if handler:
            handler(order_entity, payment_entity, event_data)

        return success("Webhook processed.")

    def _handle_payment_captured(self, order_data: dict, payment_data: dict, event_data: dict):
        """Handle payment.captured event (payment completed)."""
        self._mark_payment_status(order_data, payment_data, target_status="PAID")

    def _handle_payment_authorized(self, order_data: dict, payment_data: dict, event_data: dict):
        """Handle payment.authorized event (payment authorized but not captured)."""
        self._mark_payment_status(order_data, payment_data, target_status="PENDING")

    def _handle_payment_failed(self, order_data: dict, payment_data: dict, event_data: dict):
        """Handle payment.failed event."""
        self._mark_payment_status(order_data, payment_data, target_status="FAILED")

    def _mark_payment_status(self, order_data: dict, payment_data: dict, target_status: str):
        """Locate the payment by gateway order id and update its status idempotently."""
        order_id = payment_data.get("order_id") or order_data.get("id")
        razorpay_payment_id = payment_data.get("id")
        gateway_status = payment_data.get("status")
        payment_amount = payment_data.get("amount")

        if not order_id:
            return

        payments_collection = get_collection(Collections.PAYMENTS)
        payment = payments_collection.find_one({"gateway_order_id": order_id})
        if not payment:
            return

        # Idempotency: skip if this exact gateway payment was already recorded.
        if payment.get("gateway_payment_id") and str(payment.get("gateway_payment_id")) == str(razorpay_payment_id):
            return

        if payment.get("status") in ("PAID", "CANCELLED"):
            return

        mapped_status = razorpay_gateway.map_payment_status(gateway_status) or target_status

        updates = {
            "status": mapped_status,
            "gateway_payment_id": razorpay_payment_id,
            "updated_at": datetime.utcnow(),
        }
        if mapped_status == "PAID":
            updates["payment_date"] = datetime.utcnow()

        payments_collection.update_one(
            {"gateway_order_id": order_id},
            {"$set": updates},
        )

        log_activity(
            module="PAYMENT",
            action="PAYMENT_VERIFIED" if mapped_status == "PAID" else "PAYMENT_FAILED",
            performed_by=payment.get("paid_by"),
            target_id=str(payment.get("_id")),
            status="SUCCESS" if mapped_status == "PAID" else "FAILED",
            description=(
                f"Payment verified via webhook: {payment.get('amenity_name')}."
                if mapped_status == "PAID"
                else f"Payment failed via webhook: {payment.get('amenity_name')}."
            ),
            metadata={
                "employee_id": payment.get("employee_id"),
                "amenity_id": payment.get("amenity_id"),
                "amount": payment.get("amount"),
                "gateway": "RAZORPAY",
                "gateway_payment_id": razorpay_payment_id,
                "gateway_status": gateway_status,
                "payment_amount": payment_amount,
            },
        )


class PaymentCallbackView(APIView):
    """Payment callback endpoint (Razorpay redirect)."""

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        """Handle gateway redirect after payment."""
        order_id = request.query_params.get("order_id")
        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000")
        if order_id:
            return redirect(f"{frontend_url}/payments?order_id={order_id}")
        return redirect(f"{frontend_url}/payments")


class AmenityView(APIView):
    """Amenity endpoints for admin management.

    Amenities define the office items/services employees can pay for.
    Only SUPER_ADMIN and ADMIN can create/update/delete amenities.
    All authenticated roles can list and view active amenities.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.amenity_service = AmenityService()

    @require_role("SUPER_ADMIN", "ADMIN")
    def post(self, request):
        """Create a new amenity."""
        serializer = AmenityCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = {
            "name": serializer.validated_data["name"],
            "description": serializer.validated_data.get("description", ""),
            "amount": serializer.validated_data["amount"],
            "created_by": str(request.user["_id"]),
        }

        amenity = self.amenity_service.create_amenity(data)

        return success("Amenity created.", {"amenity": amenity}, status_code=status.HTTP_201_CREATED)

    @require_role("SUPER_ADMIN", "ADMIN", "HR_MANAGER", "EMPLOYEE")
    def get(self, request, amenity_id=None):
        """List amenities or get a single amenity."""
        if amenity_id:
            amenity = self.amenity_service.get_active_amenity(amenity_id)
            return success(data={"amenity": amenity})

        include_inactive = request.query_params.get("include_inactive", "false").lower() == "true"
        amenities = self.amenity_service.list_amenities(include_inactive=include_inactive)

        return success(data={"amenities": amenities})

    @require_role("SUPER_ADMIN", "ADMIN")
    def put(self, request, amenity_id):
        """Update an amenity."""
        serializer = AmenityUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amenity = self.amenity_service.update_amenity(amenity_id, serializer.validated_data)

        return success("Amenity updated.", {"amenity": amenity})

    @require_role("SUPER_ADMIN", "ADMIN")
    def delete(self, request, amenity_id):
        """Soft delete an amenity."""
        self.amenity_service.delete_amenity(amenity_id, user_id=str(request.user["_id"]))

        return success("Amenity deleted.")
