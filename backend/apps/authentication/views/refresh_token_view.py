"""
Refresh Token View.
Handles HTTP API requests for token refresh.
"""
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from apps.authentication.services.auth_service import AuthService


class RefreshTokenView(APIView):
    """Handle refresh token requests."""

    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response(
                {"success": False, "message": "Refresh token is required.", "errors": None},
                status=status.HTTP_400_BAD_REQUEST,
            )
        service = AuthService()
        result = service.refresh_token(refresh_token)
        return Response(
            {"success": True, "message": "Token refreshed successfully.", "data": result},
            status=status.HTTP_200_OK,
        )