"""
Cashfree Webhook Controller.
Handles Cashfree webhook events for reliable payment notifications.

Webhooks ensure the backend receives payment events even if:
- browser closes after payment
- network fails during callback
- frontend callback fails
- user leaves the page after payment
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.common.config.settings import settings
from apps.common.database.mongo import mongo
from apps.payment.gateways.cashfree_gateway import cashfree_gateway
from apps.payment.repositories.payment_repository import PaymentRepository

logger = logging.getLogger(__name__)


class CashfreeWebhookController(APIView):
    """
    Cashfree webhook endpoint.
    
    Cashfree sends webhook events to this endpoint for payment status updates.
    We verify the webhook signature to ensure authenticity.
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        """Handle incoming Cashfree webhook events."""
        signature = request.headers.get("x-webhook-signature")
        timestamp = request.headers.get("x-webhook-timestamp")

        if not signature or not timestamp:
            return Response(
                {"error": "Missing signature or timestamp"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        raw_body = request.body
        if not isinstance(raw_body, bytes):
            raw_body = raw_body.encode("utf-8")

        if not cashfree_gateway.verify_webhook_signature(signature, raw_body.decode("utf-8"), timestamp):
            return Response(
                {"error": "Invalid signature"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            event_data = json.loads(raw_body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return Response(
                {"error": "Invalid JSON"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        event_type = event_data.get("type")
        payload_data = event_data.get("data", {})
        order_data = payload_data.get("order", {})
        payment_data = payload_data.get("payment", {})
        customer_details = payload_data.get("customer_details", {})

        handlers = {
            "PAYMENT_SUCCESS_WEBHOOK": self._handle_payment_success,
            "PAYMENT_FAILED_WEBHOOK": self._handle_payment_failed,
            "PAYMENT_USER_DROPPED_WEBHOOK": self._handle_payment_user_dropped,
        }

        handler = handlers.get(event_type)
        if handler:
            handler(order_data, payment_data, customer_details, event_data)

        return Response({"status": "ok"}, status=status.HTTP_200_OK)

    def _handle_payment_success(self, order_data: dict, payment_data: dict, customer_details: dict, event_data: dict):
        """Handle PAYMENT_SUCCESS_WEBHOOK event."""
        order_id = order_data.get("order_id")
        cf_payment_id = payment_data.get("cf_payment_id")
        payment_status = payment_data.get("payment_status")
        payment_amount = payment_data.get("payment_amount")
        payment_time = payment_data.get("payment_time")

        if not order_id or not cf_payment_id:
            return

        repository = PaymentRepository()
        payment = repository.get_by_order_id(order_id)
        if not payment:
            return

        if payment.get("status") == "PAID":
            return

        collection = mongo.get_collection("payments")
        from datetime import datetime

        updates = {
            "status": "PAID",
            "gateway_payment_id": str(cf_payment_id),
            "payment_date": payment_time or datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow(),
        }
        collection.update_one(
            {"gateway_order_id": order_id},
            {"$set": updates},
        )

        activity_collection = mongo.get_collection("activity_logs")
        activity_collection.insert_one({
            "module": "PAYMENT",
            "action": "PAYMENT_VERIFIED",
            "performed_by": payment.get("paid_by"),
            "target_id": str(payment.get("_id")),
            "status": "SUCCESS",
            "description": f"Payment verified via webhook: {payment.get('amenity_name')}.",
            "metadata": {
                "employee_id": payment.get("employee_id"),
                "amenity_id": payment.get("amenity_id"),
                "amount": payment.get("amount"),
                "gateway_payment_id": str(cf_payment_id),
                "payment_status": payment_status,
                "payment_amount": payment_amount,
            },
            "created_at": datetime.utcnow(),
        })

    def _handle_payment_failed(self, order_data: dict, payment_data: dict, customer_details: dict, event_data: dict):
        """Handle PAYMENT_FAILED_WEBHOOK event."""
        order_id = order_data.get("order_id")
        cf_payment_id = payment_data.get("cf_payment_id")

        if not order_id:
            return

        repository = PaymentRepository()
        payment = repository.get_by_order_id(order_id)
        if not payment:
            return

        if payment.get("status") in ("PAID", "FAILED", "CANCELLED"):
            return

        collection = mongo.get_collection("payments")
        from datetime import datetime

        collection.update_one(
            {"gateway_order_id": order_id},
            {
                "$set": {
                    "status": "FAILED",
                    "gateway_payment_id": str(cf_payment_id) if cf_payment_id else payment.get("gateway_payment_id"),
                    "updated_at": datetime.utcnow(),
                }
            },
        )

        activity_collection = mongo.get_collection("activity_logs")
        activity_collection.insert_one({
            "module": "PAYMENT",
            "action": "PAYMENT_FAILED",
            "performed_by": payment.get("paid_by"),
            "target_id": str(payment.get("_id")),
            "status": "FAILED",
            "description": f"Payment failed via webhook: {payment.get('amenity_name')}.",
            "created_at": datetime.utcnow(),
        })

    def _handle_payment_user_dropped(self, order_data: dict, payment_data: dict, customer_details: dict, event_data: dict):
        """Handle PAYMENT_USER_DROPPED_WEBHOOK event."""
        order_id = order_data.get("order_id")
        cf_payment_id = payment_data.get("cf_payment_id")

        if not order_id:
            return

        repository = PaymentRepository()
        payment = repository.get_by_order_id(order_id)
        if not payment:
            return

        if payment.get("status") in ("PAID", "FAILED", "CANCELLED"):
            return

        collection = mongo.get_collection("payments")
        from datetime import datetime

        collection.update_one(
            {"gateway_order_id": order_id},
            {
                "$set": {
                    "status": "FAILED",
                    "gateway_payment_id": str(cf_payment_id) if cf_payment_id else payment.get("gateway_payment_id"),
                    "updated_at": datetime.utcnow(),
                }
            },
        )

        activity_collection = mongo.get_collection("activity_logs")
        activity_collection.insert_one({
            "module": "PAYMENT",
            "action": "PAYMENT_FAILED",
            "performed_by": payment.get("paid_by"),
            "target_id": str(payment.get("_id")),
            "status": "FAILED",
            "description": f"Payment dropped via webhook: {payment.get('amenity_name')}.",
            "created_at": datetime.utcnow(),
        })
