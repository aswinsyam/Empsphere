"""
Authentication View.
Handles HTTP API requests for authentication flows.
"""
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from apps.authentication.services.auth_service import AuthService
from apps.authentication.serializers.auth_serializer import AuthSerializer
from apps.common.responses.api_response import ApiResponse


class AuthView(APIView):
    """Handle authentication-related API requests."""

    def post(self, request):
        serializer = AuthSerializer(data=request.data)
        if serializer.is_valid():
            service = AuthService()
            result = service.register(serializer.validated_data)
            return ApiResponse.success(
                message="Registration initiated.",
                data={"requires_otp": result.get("requires_otp", True)},
                status_code=status.HTTP_201_CREATED,
            )
        return ApiResponse.error(
            message="Validation error",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )