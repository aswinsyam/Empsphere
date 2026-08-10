"""
Custom JWT authentication for Django REST Framework.

Authenticates requests using the Bearer access token and
attaches the authenticated user payload to the request.
"""

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

import jwt

from apps.common.config.settings import settings
from apps.authentication.repositories.user_repository import UserRepository


class JWTAuthentication(BaseAuthentication):
    """Authenticate users via a Bearer JWT access token."""

    def authenticate(self, request):
        header = request.META.get("HTTP_AUTHORIZATION", "")

        if not header.startswith("Bearer "):
            return None

        token = header.split(" ", 1)[1]

        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM],
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Access token has expired.")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid access token.")

        if payload.get("token_type") != "access":
            raise AuthenticationFailed("Invalid token type.")

        user_id = payload.get("user_id")

        if not user_id:
            raise AuthenticationFailed("Invalid token payload.")

        user = UserRepository().get_by_id(user_id)

        if not user:
            raise AuthenticationFailed("User not found.")

        return (user, token)

    def authenticate_header(self, request):
        return 'Bearer realm="api"'
