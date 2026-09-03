"""
JWT authentication for Django REST Framework.

Flow:
    1. Read ``Authorization: Bearer <access_token>`` from the request.
    2. Decode and validate the JWT (signature + expiry).
    3. Check ``token_type == "access"``.
    4. Load the user document from MongoDB by ``user_id``.
    5. Attach ``(user_document, token)`` to ``request.auth``.

This class only answers **WHO the user is**.  What they are allowed to do
is decided by ``common.permissions.require_role`` or ``IsAuthenticatedUser``.
"""

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

import jwt
from bson import ObjectId

from apps.common.settings import settings
from apps.common.database import get_collection
from apps.common.constants import Collections


class JWTAuthentication(BaseAuthentication):
    """Authenticate requests using a Bearer JWT access token."""

    def authenticate(self, request):
        header = request.META.get("HTTP_AUTHORIZATION", "")
        if not header.startswith("Bearer "):
            return None

        token = header.split(" ", 1)[1]

        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET,
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

        user = get_collection(Collections.USERS).find_one({"_id": ObjectId(user_id)})
        if not user:
            raise AuthenticationFailed("User not found.")

        return (user, token)

    def authenticate_header(self, request):
        return 'Bearer realm="api"'
