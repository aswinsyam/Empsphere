"""
Payment app URL routes.
"""
from django.urls import path

from apps.payment.amenities.amenity_controller import AmenityController
from apps.payment.controllers.callback_controller import PaymentCallbackController
from apps.payment.controllers.payment_controller import (
    PaymentCancelController,
    PaymentController,
    PaymentVerifyController,
)
from apps.payment.controllers.webhook_controller import CashfreeWebhookController

urlpatterns = [
    # Payment callback endpoint (for Cashfree return_url redirects)
    path("callback/", PaymentCallbackController.as_view(), name="payment-callback"),
    # Payment endpoints
    path("", PaymentController.as_view(), name="payment-list-create"),
    path("me/", PaymentController.as_view(), name="payment-me"),
    # Amenity endpoints - MUST come before <str:payment_id>/ patterns
    path("amenities/", AmenityController.as_view(), name="amenity-list-create"),
    path("amenities/<str:amenity_id>/", AmenityController.as_view(), name="amenity-detail"),
    # Cashfree webhook endpoint - MUST come before <str:payment_id>/ patterns
    path("webhook/", CashfreeWebhookController.as_view(), name="cashfree-webhook"),
    # Payment detail routes with URL parameters
    path("<str:payment_id>/", PaymentController.as_view(), name="payment-detail"),
    path("<str:payment_id>/verify/", PaymentVerifyController.as_view(), name="payment-verify"),
    path("<str:payment_id>/cancel/", PaymentCancelController.as_view(), name="payment-cancel"),
]
