from __future__ import annotations
from rest_framework import serializers


class LeaveSerializer(serializers.Serializer):
    """Leave serialization and validation for create."""

    employee_id = serializers.CharField(required=False)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    leave_type = serializers.CharField(required=False)
    reason = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False)


class LeaveDecisionSerializer(serializers.Serializer):
    """Serializer for approve/reject actions. A reason is required."""

    status = serializers.ChoiceField(choices=["APPROVED", "REJECTED"])
    approval_reason = serializers.CharField(required=False, allow_blank=False)
    rejection_reason = serializers.CharField(required=False, allow_blank=False)

    def validate(self, attrs):
        decision = attrs.get("status")
        if decision == "APPROVED":
            reason = (attrs.get("approval_reason") or "").strip()
            if not reason:
                raise serializers.ValidationError(
                    {"approval_reason": "Approval reason is required."}
                )
            attrs["approval_reason"] = reason
            attrs["rejection_reason"] = ""
        elif decision == "REJECTED":
            reason = (attrs.get("rejection_reason") or "").strip()
            if not reason:
                raise serializers.ValidationError(
                    {"rejection_reason": "Rejection reason is required."}
                )
            attrs["rejection_reason"] = reason
            attrs["approval_reason"] = ""
        return attrs