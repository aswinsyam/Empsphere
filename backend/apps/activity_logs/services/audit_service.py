"""
Audit Service.
Records audit log entries.
"""
from __future__ import annotations

from apps.common.database.mongo import mongo
from apps.common.core.collections import Collections


class AuditService:
    """Writes audit records to MongoDB."""

    def __init__(self):
        self.collection = mongo.get_collection(Collections.ACTIVITY_LOGS)

    def log(self, module, action, performed_by, target_id, status, description, metadata=None):
        """Insert an audit log document into MongoDB."""
        from datetime import datetime
        self.collection.insert_one({
            "module": module,
            "action": action,
            "performed_by": performed_by,
            "target_id": target_id,
            "status": status,
            "description": description,
            "metadata": metadata or {},
            "created_at": datetime.utcnow(),
        })