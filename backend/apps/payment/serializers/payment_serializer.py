"""
Payment Serializer.
DRF serializer for office payment.
"""
from __future__ import annotations

from rest_framework import serializers


class PaymentCreateSerializer(serializers.Serializer):
    """Payment serialization and validation for create."""

    employee_id = serializers.CharField(required=False, allow_blank=True)
    amenity_id = serializers.CharField(required=True)


class PaymentVerifySerializer(serializers.Serializer):
    """Payment verification serializer."""

    gateway_order_id = serializers.CharField(max_length=255)
    gateway_payment_id = serializers.CharField(max_length=255)
    payment_status = serializers.CharField(max_length=50, required=False)
