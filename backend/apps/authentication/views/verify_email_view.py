"""
Verify Email View.
Handles HTTP API requests for email verification.
"""
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from apps.authentication.services.auth_service import AuthService
from apps.authentication.serializers.otp_serializer import VerifyOTPSerializer
from apps.common.responses.api_response import ApiResponse


class VerifyEmailView(APIView):
    """Handle email verification requests."""

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            service = AuthService()
            result = service.verify_email(serializer.validated_data)
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