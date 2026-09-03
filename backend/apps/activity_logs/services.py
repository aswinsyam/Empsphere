"""
Activity log service.

One reusable function — any module can call it:

    from apps.activity_logs.services import log_activity
    log_activity("EMPLOYEE", "CREATE", user_id, new_id, "SUCCESS", "Created employee …")
"""

from datetime import datetime

from apps.common.database import get_collection
from apps.common.constants import Collections


def log_activity(module, action, performed_by, target_id, status, description, metadata=None):
    """Insert an audit log document into MongoDB."""
    get_collection(Collections.ACTIVITY_LOGS).insert_one({
        "module": module,
        "action": action,
        "performed_by": performed_by,
        "target_id": target_id,
        "status": status,
        "description": description,
        "metadata": metadata or {},
        "created_at": datetime.utcnow(),
    })
