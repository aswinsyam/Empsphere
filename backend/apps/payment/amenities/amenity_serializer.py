"""
Amenity Serializer.
DRF serializer for office amenities.
"""
from __future__ import annotations

from rest_framework import serializers


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
