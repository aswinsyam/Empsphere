from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any

import requests

from apps.common.settings import settings


class RazorpayGateway:
    """Razorpay payment gateway integration.

    Razorpay uses HTTP Basic auth (key_id / key_secret) and amounts expressed in
    the smallest currency unit (paise for INR). Webhook signatures are computed
    with HMAC-SHA256 over the raw request body using the webhook secret.
    """

    gateway_name = "RAZORPAY"
    webhook_path = "razorpay"

    def __init__(self):
        self.key_id = settings.RAZORPAY_KEY_ID
        self.key_secret = settings.RAZORPAY_KEY_SECRET
        self.webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
        self.environment = settings.RAZORPAY_ENVIRONMENT or "TEST"

        # Razorpay serves test and live traffic from the same host; the key
        # pair and webhook secret determine the mode.
        self.base_url = "https://api.razorpay.com/v1"

        self.session = requests.Session()
        self.session.auth = (self.key_id, self.key_secret)
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def create_order(
        self,
        amount: float,
        currency: str = "INR",
        receipt: str = None,
        customer_details: dict = None,
        return_url: str = None,
        notify_url: str = None,
    ) -> dict[str, Any]:
        """Create a Razorpay order.

        ``amount`` is supplied in major currency units (e.g. INR rupees) and is
        converted to paise internally. ``customer_details``, ``return_url`` and
        ``notify_url`` are attached to the order as notes for traceability.
        """
        order_id = receipt or f"order_{int(time.time())}"

        payload: dict[str, Any] = {
            "amount": int(round(amount * 100)),
            "currency": currency,
            "receipt": order_id,
            "payment_capture": 1,
        }

        notes = {}
        if customer_details:
            notes["customer_details"] = json.dumps(customer_details, default=str)
        if return_url:
            notes["return_url"] = return_url
        if notify_url:
            notes["notify_url"] = notify_url
        if notes:
            payload["notes"] = notes

        url = f"{self.base_url}/orders"
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return {
            "order_id": data.get("id") or data.get("order_id"),
            "key_id": self.key_id,
        }

    def get_order(self, order_id: str) -> dict[str, Any]:
        """Get Razorpay order details."""
        url = f"{self.base_url}/orders/{order_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_order_payments(self, order_id: str) -> list[dict[str, Any]]:
        """Get payments linked to a Razorpay order.

        Returns a normalized list with ``payment_id``, ``status``, ``amount``
        and ``currency`` keys.
        """
        url = f"{self.base_url}/orders/{order_id}"
        response = self.session.get(url, params={"expand[]": "payments"})
        response.raise_for_status()
        data = response.json()

        order_payments = data.get("payments", []) if isinstance(data, dict) else []
        normalized = []
        for p in order_payments:
            normalized.append({
                "payment_id": p.get("id"),
                "status": p.get("status"),
                "amount": p.get("amount"),
                "currency": p.get("currency", "INR"),
            })
        return normalized

    def verify_payment_signature(
        self,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str,
    ) -> bool:
        """Verify a Razorpay Checkout success signature.

        Razorpay signs ``order_id|payment_id`` with the key secret using
        HMAC-SHA256. The frontend submits these three values; the backend
        recomputes the signature and compares it in constant time.
        """
        if not (self.key_secret and razorpay_order_id and razorpay_payment_id and razorpay_signature):
            return False
        payload = f"{razorpay_order_id}|{razorpay_payment_id}".encode("utf-8")
        expected = hmac.new(
            self.key_secret.encode("utf-8"),
            payload,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, razorpay_signature or "")

    def verify_webhook_signature(self, signature: str, raw_body: str) -> bool:
        """Verify Razorpay webhook signature.

        ``X-Razorpay-Signature`` is HMAC-SHA256(raw_body) using the webhook
        secret.
        """
        if not self.webhook_secret:
            return False
        body = raw_body.encode("utf-8") if isinstance(raw_body, str) else raw_body
        expected = hmac.new(
            self.webhook_secret.encode("utf-8"),
            body,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature or "")

    @staticmethod
    def map_payment_status(gateway_status: str) -> str:
        """Map Razorpay payment status to EmpSphere internal status."""
        status_map = {
            "created": "PENDING",
            "authorized": "PENDING",
            "captured": "PAID",
            "succeeded": "PAID",
            "paid": "PAID",
            "failed": "FAILED",
            "error": "FAILED",
            "pending": "PENDING",
            "refunded": "REFUNDED",
            "cancelled": "CANCELLED",
        }
        return status_map.get((gateway_status or "").lower(), "PENDING")


razorpay_gateway = RazorpayGateway()
