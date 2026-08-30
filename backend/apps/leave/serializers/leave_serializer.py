"""
Leave Serializer.
DRF serializer for leave.
"""
from __future__ import annotations
from rest_framework import serializers


class LeaveSerializer(serializers.Serializer):
    """Leave serialization and validation for create/update."""

    employee_id = serializers.CharField(required=False)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    leave_type = serializers.CharField(required=False)
    reason = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False)


class LeaveDetailSerializer(serializers.Serializer):
    """Leave detail serializer for read operations."""

    leave_id = serializers.CharField(source="_id")
    employee_id = serializers.CharField()
    employee_name = serializers.CharField(required=False)
    employee_code = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    leave_type = serializers.CharField()
    reason = serializers.CharField(required=False)
    status = serializers.CharField()
    approved_by = serializers.CharField(required=False)
    rejected_by = serializers.CharField(required=False)
    created_at = serializers.DateTimeField(required=False)
    updated_at = serializers.DateTimeField(required=False)
