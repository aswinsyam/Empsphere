"""
Audit View.
Handles audit log API requests.
"""
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from apps.activity_logs.services.audit_service import AuditService


class AuditView(APIView):
    """Handle audit log requests."""

    def post(self, request):
        service = AuditService()
        service.log(
            module=request.data.get("module"),
            action=request.data.get("action"),
            performed_by=request.data.get("performed_by"),
            target_id=request.data.get("target_id"),
            status=request.data.get("status"),
            description=request.data.get("description"),
            metadata=request.data.get("metadata", {}),
        )
        return Response(
            {"success": True, "message": "Audit log recorded successfully.", "status_code": status.HTTP_201_CREATED},
            status=status.HTTP_201_CREATED,
        )