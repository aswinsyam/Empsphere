"""
Verify Email View.
Handles HTTP API requests for email verification via OTP.
"""
from rest_framework.views import APIView
from rest_framework import status

from apps.authentication.services.otp_service import OTPService
from apps.authentication.serializers.otp_serializer import VerifyOTPSerializer
from apps.common.responses.api_response import ApiResponse


class VerifyEmailView(APIView):
    """Handle email verification requests via OTP."""

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            service = OTPService()
            result = service.verify_otp(serializer.validated_data)
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
