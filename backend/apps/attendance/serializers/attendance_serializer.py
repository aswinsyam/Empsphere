"""
Attendance Serializer.
DRF serializer for attendance.
"""
from __future__ import annotations
from rest_framework import serializers


class AttendanceSerializer(serializers.Serializer):
    """Attendance serialization and validation for create."""

    employee_id = serializers.CharField(required=False)
    date = serializers.DateField()
    status = serializers.CharField(required=False)
    check_in = serializers.DateTimeField(required=False, allow_null=True)
    check_out = serializers.DateTimeField(required=False, allow_null=True)
    remarks = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        """Validate that check_in is before check_out when both are provided."""
        check_in = attrs.get("check_in")
        check_out = attrs.get("check_out")
        if check_in and check_out:
            if check_in >= check_out:
                raise serializers.ValidationError(
                    {"check_out": "Check-out time must be after check-in time."}
                )
        return attrs


class AttendanceUpdateSerializer(serializers.Serializer):
    """Attendance update serializer — only mutable fields."""

    status = serializers.CharField(required=False)
    check_in = serializers.DateTimeField(required=False, allow_null=True)
    check_out = serializers.DateTimeField(required=False, allow_null=True)
    remarks = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        """Validate that check_in is before check_out when both are provided."""
        check_in = attrs.get("check_in")
        check_out = attrs.get("check_out")
        if check_in and check_out:
            if check_in >= check_out:
                raise serializers.ValidationError(
                    {"check_out": "Check-out time must be after check-in time."}
                )
        return attrs


class CheckInSerializer(serializers.Serializer):
    """Serializer for check-in action — no input fields required."""

    pass


class CheckOutSerializer(serializers.Serializer):
    """Serializer for check-out action — no input fields required."""

    pass
