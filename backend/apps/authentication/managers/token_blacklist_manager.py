"""
Token blacklist manager.

Stores revoked refresh tokens in the tokens collection using a
duplicate-safe, jti-based index. An optional TTL index is created lazily
so expired revocations are automatically cleaned up by MongoDB.
"""

from datetime import datetime

import jwt

from apps.common.config.settings import settings
from apps.common.database.mongo import mongo
from apps.common.core.collections import Collections


class TokenBlacklistManager:
    """Blacklists refresh tokens on logout."""

    def __init__(self):
        self.collection = mongo.get_collection(Collections.TOKENS)
        self._ensure_indexes()

    def _ensure_indexes(self) -> None:
        """
        Create required indexes idempotently:
        - unique index on ``jti`` so blacklisting is duplicate-safe
        - TTL index on ``expires_at`` so revoked tokens auto-expire
        """
        self.collection.create_index("jti", unique=True)
        self.collection.create_index(
            "expires_at",
            expireAfterSeconds=0,
        )

    def blacklist(self, token: str) -> None:
        """
        Revoke a refresh token.

        The token is stored as a SHA-256 hash (never the raw token) and
        keyed by its ``jti`` claim. Insertion is duplicate-safe: if the
        token is already blacklisted, the operation is a no-op.
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM],
            )
        except jwt.InvalidTokenError:
            # Do not persist malformed tokens; nothing to revoke.
            return

        jti = payload.get("jti")
        if not jti:
            return

        expires_at = None
        exp = payload.get("exp")
        if isinstance(exp, (int, float)):
            expires_at = datetime.utcfromtimestamp(exp)

        self.collection.update_one(
            {"jti": jti},
            {
                "$setOnInsert": {
                    "jti": jti,
                    "token_hash": self._hash_token(token),
                    "revoked": True,
                    "created_at": datetime.utcnow(),
                    "expires_at": expires_at,
                }
            },
            upsert=True,
        )

    def is_blacklisted(self, token: str) -> bool:
        """
        Return True if the refresh token has been revoked.

        Falls back to matching the raw token for any legacy entries that
        predate the jti-based index.
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM],
            )
        except jwt.InvalidTokenError:
            # Invalid tokens are treated as not blacklisted; upstream
            # validation will reject them on token_type/payload checks.
            return False

        jti = payload.get("jti")
        if jti:
            exists = self.collection.find_one({"jti": jti, "revoked": True})
            if exists:
                return True

        return self.collection.find_one(
            {"token_hash": self._hash_token(token), "revoked": True}
        ) is not None

    @staticmethod
    def _hash_token(token: str) -> str:
        """Return a SHA-256 hash of the token for secure storage."""
        import hashlib

        return hashlib.sha256(token.encode("utf-8")).hexdigest()
