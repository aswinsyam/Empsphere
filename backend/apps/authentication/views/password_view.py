"""
Password View.
Handles HTTP API requests for password operations.
"""
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from apps.authentication.services.password_service import PasswordService
from apps.authentication.serializers.password_serializer import PasswordSerializer
from apps.common.responses.api_response import ApiResponse


class PasswordView(APIView):
    """Handle password-related API requests."""

    def post(self, request):
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            service = PasswordService()
            result = service.update_password(serializer.validated_data)
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