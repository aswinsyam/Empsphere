"""
Google Login View.
Handles HTTP API requests for Google authentication.
"""
from rest_framework.views import APIView
from rest_framework import status

from apps.common.security.google_manager import GoogleManager
from apps.authentication.serializers.auth_serializer import GoogleLoginSerializer


class GoogleLoginView(APIView):
    """Handle Google login requests."""

    def post(self, request):
        serializer = GoogleLoginSerializer(data=request.data)
        if serializer.is_valid():
            service = GoogleManager()
            info = service.verify_id_token(serializer.validated_data["id_token"])
            if not info:
                from apps.common.exceptions.custom_exception import UnauthorizedException
                raise UnauthorizedException("Invalid Google token.")
            user_info = GoogleManager.extract_user_info(info)
            user = self._get_or_create_google_user(user_info)
            access_token, refresh_token = self._generate_tokens(user)
            return self.success(
                message="Google login successful.",
                data={"user_id": str(user["_id"]), "email": user["email"], "role": user["role"], "access_token": access_token, "refresh_token": refresh_token},
                status_code=status.HTTP_200_OK,
            )
        return self.error(message=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

    def _get_or_create_google_user(self, user_info):
        """Get existing user or create new one from Google auth."""
        from apps.authentication.repositories.user_repository import UserRepository
        user_repo = UserRepository()
        user = user_repo.get_by_google_id(user_info["google_id"])
        if user:
            user_repo.update(str(user["_id"]), {"google_id": user_info["google_id"], "is_email_verified": True})
            return user
        document = {
            "employee_code": None,
            "first_name": user_info["first_name"],
            "last_name": user_info["last_name"],
            "full_name": user_info["full_name"],
            "email": user_info["email"],
            "phone": "",
            "password": None,
            "role": "EMPLOYEE",
            "department_id": None,
            "designation_id": None,
            "login_provider": "GOOGLE",
            "google_id": user_info["google_id"],
            "profile_image": user_info["profile_image"],
            "is_email_verified": True,
        }
        user_id = user_repo.create(document)
        return user_repo.get_by_id(user_id)

    def _generate_tokens(self, user):
        """Generate JWT access and refresh tokens."""
        import jwt
        from apps.common.config.settings import settings
        from datetime import datetime, timedelta, timezone
        import uuid

        access_payload = {
            "user_id": str(user["_id"]),
            "email": user.get("email"),
            "role": user.get("role"),
            "token_type": "access",
            "jti": str(uuid4()),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
            "iat": datetime.now(timezone.utc),
        }
        refresh_payload = {
            "user_id": str(user["_id"]),
            "email": user.get("email"),
            "role": user.get("role"),
            "token_type": "refresh",
            "jti": str(uuid4()),
            "exp": datetime.now(timezone.utc) + timedelta(days=7),
            "iat": datetime.now(timezone.utc),
        }
        access_token = jwt.encode(access_payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        refresh_token = jwt.encode(refresh_payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        return access_token, refresh_token