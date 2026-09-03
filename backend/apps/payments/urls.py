from django.urls import path

from apps.payments.views import (
    AmenityView,
    PaymentCallbackView,
    PaymentCancelView,
    PaymentVerifyView,
    PaymentView,
    RazorpayWebhookView,
)

urlpatterns = [
    # Payment callback endpoint (for gateway return_url redirects)
    path("callback/", PaymentCallbackView.as_view(), name="payment-callback"),
    # Payment endpoints
    path("", PaymentView.as_view(), name="payment-list-create"),
    path("me/", PaymentView.as_view(), name="payment-me"),
    # Amenity endpoints - MUST come before <str:payment_id>/ patterns
    path("amenities/", AmenityView.as_view(), name="amenity-list-create"),
    path("amenities/<str:amenity_id>/", AmenityView.as_view(), name="amenity-detail"),
    # Razorpay webhook endpoint - MUST come before <str:payment_id>/ patterns
    path("webhook/razorpay/", RazorpayWebhookView.as_view(), name="razorpay-webhook"),
    # Payment detail routes with URL parameters
    path("<str:payment_id>/", PaymentView.as_view(), name="payment-detail"),
    path("<str:payment_id>/verify/", PaymentVerifyView.as_view(), name="payment-verify"),
    path("<str:payment_id>/cancel/", PaymentCancelView.as_view(), name="payment-cancel"),
]
