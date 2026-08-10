"""
Audit service.

Records audit log entries to the activity_logs collection.
"""

from __future__ import annotations

from apps.common.database.mongo import mongo
from apps.common.core.collections import Collections


class AuditService:
    """Writes audit records to MongoDB."""

    def __init__(self):
        self.collection = mongo.get_collection(Collections.ACTIVITY_LOGS)

    def log(
        self,
        module: str,
        action: str,
        performed_by: str,
        target_id: str,
        status: str,
        description: str,
        metadata: dict | None = None,
    ) -> None:
        """Insert an audit log document."""
        self.collection.insert_one(
            {
                "module": module,
                "action": action,
                "performed_by": performed_by,
                "target_id": target_id,
                "status": status,
                "description": description,
                "metadata": metadata or {},
                "created_at": __import__("datetime").datetime.utcnow(),
            }
        )
