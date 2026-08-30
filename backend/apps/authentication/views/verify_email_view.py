"""
Verify Email View.
Handles HTTP API requests for email verification via OTP.
"""
from rest_framework.views import APIView
from rest_framework import status

from rest_framework.permissions import AllowAny

from apps.authentication.services.auth_service import AuthService
from apps.authentication.serializers.otp_serializer import VerifyOTPSerializer
from apps.common.responses.api_response import ApiResponse


class VerifyEmailView(APIView):
    """Handle email verification requests via OTP."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Verify an email address using a one-time OTP code."""
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            auth_service = AuthService()
            result = auth_service.verify_first_login(serializer.validated_data)
            return ApiResponse.success(
                message=result["message"],
                data=result,
                status_code=status.HTTP_200_OK,
            )
        return ApiResponse.error(
            message="Validation error",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )