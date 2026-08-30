"""
Payment Callback Controller.
Handles Cashfree return_url redirects after payment.
"""
from __future__ import annotations

from django.shortcuts import redirect
from rest_framework.views import APIView

from apps.common.config.settings import settings


class PaymentCallbackController(APIView):
    """Cashfree payment callback endpoint."""

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        """Handle Cashfree redirect after payment."""
        order_id = request.query_params.get("order_id")
        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000")
        if order_id:
            return redirect(f"{frontend_url}/payments?order_id={order_id}")
        return redirect(f"{frontend_url}/payments")
