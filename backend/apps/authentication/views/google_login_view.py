"""
Google Login View.
Handles HTTP API requests for Google authentication.
"""
from rest_framework.views import APIView
from rest_framework import status

from rest_framework.permissions import AllowAny

from apps.authentication.services.auth_service import AuthService
from apps.authentication.serializers.auth_serializer import GoogleLoginSerializer
from apps.common.responses.api_response import ApiResponse


class GoogleLoginView(APIView):
    """Handle Google login requests."""
    permission_classes = [AllowAny]

    def post(self, request):
        """Authenticate a user via a Google ID token."""
        serializer = GoogleLoginSerializer(data=request.data)
        if serializer.is_valid():
            service = AuthService()
            result = service.google_login(serializer.validated_data)
            return ApiResponse.success(
                message="Google login successful.",
                data=result,
                status_code=status.HTTP_200_OK,
            )
        return ApiResponse.error(
            message="Validation error",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )