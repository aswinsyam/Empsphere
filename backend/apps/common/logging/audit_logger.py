"""
Audit logger.

Records security and compliance related events.
"""

import logging

logger = logging.getLogger("apps")


class AuditLogger:
    """Writes audit log entries."""

    @staticmethod
    def log(module: str, action: str, user_id: str, description: str):
        logger.info(
            "AUDIT module=%s action=%s user=%s description=%s",
            module,
            action,
            user_id,
            description,
        )
