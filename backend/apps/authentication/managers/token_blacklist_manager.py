"""
Token Blacklist Manager.
Manages JWT token blacklisting.
"""
from __future__ import annotations
import jwt
from datetime import datetime, timedelta
from apps.common.base.base_manager import BaseManager
from apps.common.config.settings import settings


class TokenBlacklistManager(BaseManager):
    """Token blacklist management."""

    def __init__(self):
        super().__init__()
        self.blacklisted_tokens = set()

    def blacklist(self, refresh_token):
        """Blacklist a refresh token."""
        try:
            payload = jwt.decode(refresh_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            self.blacklisted_tokens.add(refresh_token)
        except Exception:
            pass

    def is_blacklisted(self, refresh_token):
        """Check if token is blacklisted."""
        return refresh_token in self.blacklisted_tokens