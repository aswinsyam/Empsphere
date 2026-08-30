"""
Designation Serializer.
DRF serializer for designation.
"""
from __future__ import annotations
from rest_framework import serializers


class DesignationSerializer(serializers.Serializer):
    """Designation serialization and validation for create."""

    name = serializers.CharField(max_length=255)
    code = serializers.CharField(max_length=50, required=False, allow_blank=True)
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)


class DesignationUpdateSerializer(serializers.Serializer):
    """Designation update serializer — only mutable fields."""

    name = serializers.CharField(max_length=255, required=False)
    code = serializers.CharField(max_length=50, required=False, allow_blank=True)
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)
    is_active = serializers.BooleanField(required=False)
