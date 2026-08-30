"""
Google OAuth2 authentication helper.
"""

from __future__ import annotations

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from apps.common.config.settings import settings


class GoogleManager:
    """Validates Google ID tokens and returns user info."""

    @staticmethod
    def verify_id_token(token: str) -> dict | None:
        """Verify a Google ID token and return decoded claims."""
        try:
            info = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID,
            )
            return info
        except Exception:
            return None

    @staticmethod
    def extract_user_info(info: dict) -> dict:
        """Extract normalized user fields from Google claims."""
        return {
            "google_id": info.get("sub"),
            "email": info.get("email"),
            "first_name": info.get("given_name", ""),
            "last_name": info.get("family_name", ""),
            "full_name": info.get("name", ""),
            "profile_image_id": info.get("picture", ""),
        }
