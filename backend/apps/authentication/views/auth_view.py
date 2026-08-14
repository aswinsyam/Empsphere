"""
Authentication View.
Handles HTTP API requests for authentication flows.
"""
from rest_framework.views import APIView
from rest_framework import status

from apps.authentication.services.auth_service import AuthService
from apps.authentication.serializers.auth_serializer import AuthSerializer
from apps.common.responses.api_response import ApiResponse


class AuthView(APIView):
    """Handle authentication-related API requests.

    Dispatches to the correct AuthService method based on the URL path:
    - /register/  -> register
    - /login/     -> login
    - /logout/    -> logout
    """

    def post(self, request):
        path = request.path.rstrip("/")
        action = path.rsplit("/", 1)[-1]

        if action == "register":
            return self._register(request)
        elif action == "login":
            return self._login(request)
        elif action == "logout":
            return self._logout(request)
        else:
            return ApiResponse.error(
                message="Unknown auth action.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    def _register(self, request):
        serializer = AuthSerializer(data=request.data)
        if serializer.is_valid():
            service = AuthService()
            result = service.register(serializer.validated_data)
            return ApiResponse.success(
                message="Registration initiated. Please check your email to verify your account.",
                data={"user_id": str(result)},
                status_code=status.HTTP_201_CREATED,
            )
        return ApiResponse.error(
            message="Validation error",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    def _login(self, request):
        serializer = AuthSerializer(data=request.data)
        if serializer.is_valid():
            service = AuthService()
            result = service.login(serializer.validated_data)
            if result.get("requires_otp"):
                return ApiResponse.success(
                    message="OTP sent to your email. Please verify to continue.",
                    data=result,
                    status_code=status.HTTP_200_OK,
                )
            return ApiResponse.success(
                message="Login successful.",
                data=result,
                status_code=status.HTTP_200_OK,
            )
        return ApiResponse.error(
            message="Validation error",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    def _logout(self, request):
        from apps.authentication.managers.token_blacklist_manager import TokenBlacklistManager
        refresh_token = request.data.get("refresh_token")
        if refresh_token:
            TokenBlacklistManager().blacklist(refresh_token)
        return ApiResponse.success(
            message="Logged out successfully.",
            data=None,
            status_code=status.HTTP_200_OK,
        )