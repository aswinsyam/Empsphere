"""
Token Blacklist Manager.
Manages JWT token blacklisting.
"""
from __future__ import annotations

import jwt
import uuid
from datetime import datetime

from apps.common.base.base_manager import BaseManager
from apps.common.config.settings import settings
from apps.common.database.mongo import mongo
from apps.common.core.collections import Collections


class TokenBlacklistManager(BaseManager):
    """Token blacklist management."""

    def __init__(self):
        super().__init__()
        self._collection = mongo.get_collection(Collections.TOKENS)

    def blacklist(self, refresh_token):
        """Blacklist a token and report whether it is now blacklisted.

        The ``tokens`` collection carries a unique index on ``jti`` and a
        TTL index on ``expires_at``, so every document must provide a
        unique ``jti`` (tokens without a ``jti`` claim get a generated
        one) or the write is rejected as a duplicate key.
        """
        try:
            payload = jwt.decode(refresh_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        except Exception:
            return False

        document = {
            "token": refresh_token,
            "user_id": payload.get("user_id"),
            "token_type": payload.get("token_type"),
            "jti": payload.get("jti") or uuid.uuid4().hex,
            "blacklisted_at": datetime.utcnow(),
        }

        expires_at = payload.get("exp")
        if expires_at:
            # Lets the TTL index drop the record once the token itself expires.
            document["expires_at"] = datetime.utcfromtimestamp(expires_at)

        try:
            self._collection.update_one(
                {"token": refresh_token},
                {"$set": document},
                upsert=True,
            )
            return True
        except Exception:
            return self.is_blacklisted(refresh_token)

    def is_blacklisted(self, refresh_token):
        """Check if token is blacklisted."""
        return self._collection.find_one({"token": refresh_token}) is not None

    def blacklist_all_user_tokens(self, user_id):
        """Blacklist all refresh tokens for a user."""
        self._collection.update_many(
            {"user_id": user_id},
            {"$set": {"blacklisted_at": datetime.utcnow()}},
        )
