"""
Cashfree Gateway.
Handles Cashfree order creation, payment session generation,
and payment/order status verification.
"""
from __future__ import annotations

import hashlib
import hmac
import base64
import json
from typing import Any

import requests

from apps.common.config.settings import settings


class CashfreeGateway:
    """Cashfree payment gateway integration."""

    def __init__(self):
        self.app_id = settings.CASHFREE_APP_ID
        self.secret_key = settings.CASHFREE_SECRET_KEY
        self.environment = settings.CASHFREE_ENVIRONMENT or "SANDBOX"
        self.api_version = settings.CASHFREE_API_VERSION or "2025-01-01"

        if self.environment == "SANDBOX":
            self.base_url = "https://sandbox.cashfree.com/pg"
        else:
            self.base_url = "https://api.cashfree.com/pg"

        self.session = requests.Session()
        self.session.headers.update({
            "x-client-id": self.app_id,
            "x-client-secret": self.secret_key,
            "x-api-version": self.api_version,
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def create_order(self, amount: float, currency: str = "INR", receipt: str = None, customer_details: dict = None, return_url: str = None, notify_url: str = None) -> dict[str, Any]:
        """
        Create a Cashfree order.

        Args:
            amount: Amount in currency units (e.g., INR).
            currency: Currency code (default: INR).
            receipt: Receipt identifier.
            customer_details: Customer information dict.
            return_url: URL to redirect after payment.
            notify_url: Webhook URL for payment notifications.

        Returns:
            Cashfree order response containing order_id and payment_session_id.
        """
        order_id = receipt or f"order_{int(__import__('time').time())}"

        payload: dict[str, Any] = {
            "order_amount": amount,
            "order_currency": currency,
            "order_id": order_id,
        }

        if customer_details:
            payload["customer_details"] = customer_details

        if return_url:
            payload["order_meta"] = {"return_url": return_url}

        if notify_url:
            if "order_meta" not in payload:
                payload["order_meta"] = {}
            payload["order_meta"]["notify_url"] = notify_url

        url = f"{self.base_url}/orders"
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def get_order_payments(self, order_id: str) -> dict[str, Any]:
        """
        Get all payments for an order.

        Args:
            order_id: Cashfree order ID.

        Returns:
            Order payments response.
        """
        url = f"{self.base_url}/orders/{order_id}/payments"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_order(self, order_id: str) -> dict[str, Any]:
        """
        Get order details.

        Args:
            order_id: Cashfree order ID.

        Returns:
            Order details response.
        """
        url = f"{self.base_url}/orders/{order_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def verify_webhook_signature(self, signature: str, raw_body: str, timestamp: str) -> bool:
        """
        Verify Cashfree webhook signature.

        Args:
            signature: x-webhook-signature header value.
            raw_body: Raw request body string.
            timestamp: x-webhook-timestamp header value.

        Returns:
            True if signature is valid.
        """
        signature_data = timestamp + raw_body
        expected_signature = base64.b64encode(
            hmac.new(
                self.secret_key.encode("utf-8"),
                signature_data.encode("utf-8"),
                hashlib.sha256,
            ).digest()
        ).decode("utf-8")
        return hmac.compare_digest(expected_signature, signature)

    @staticmethod
    def map_payment_status(cashfree_status: str) -> str:
        """
        Map Cashfree payment status to EmpSphere internal status.

        Args:
            cashfree_status: Cashfree payment status.

        Returns:
            EmpSphere payment status.
        """
        status_map = {
            "SUCCESS": "PAID",
            "PAID": "PAID",
            "FAILED": "FAILED",
            "USER_DROPPED": "FAILED",
            "PENDING": "PENDING",
            "EXPIRED": "CANCELLED",
            "CANCELLED": "CANCELLED",
        }
        return status_map.get(cashfree_status.upper(), "PENDING")


cashfree_gateway = CashfreeGateway()
