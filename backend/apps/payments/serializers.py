from __future__ import annotations

from rest_framework import serializers


class PaymentCreateSerializer(serializers.Serializer):
    """Payment serialization and validation for create."""

    employee_id = serializers.CharField(required=False, allow_blank=True)
    amenity_id = serializers.CharField(required=True)


class PaymentVerifySerializer(serializers.Serializer):
    """Payment verification serializer (Razorpay Checkout)."""

    razorpay_order_id = serializers.CharField(max_length=255)
    razorpay_payment_id = serializers.CharField(max_length=255)
    razorpay_signature = serializers.CharField(max_length=512)


class AmenityCreateSerializer(serializers.Serializer):
    """Amenity serialization and validation for create."""

    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    amount = serializers.FloatField(min_value=1)


class AmenityUpdateSerializer(serializers.Serializer):
    """Amenity update serializer."""

    name = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    amount = serializers.FloatField(min_value=1, required=False)
