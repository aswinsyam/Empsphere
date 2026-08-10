"""
Base Service.

Provides common functionality for all services.
"""

from __future__ import annotations

from typing import Any

from apps.activity_logs.services.audit_service import AuditService


class BaseService:
    """
    Base class for all services.
    """

    def __init__(self):
        self.audit_service = AuditService()

    def log_activity(
        self,
        module: str,
        action: str,
        performed_by: str,
        target_id: str,
        status: str,
        description: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Write an audit log.
        """

        self.audit_service.log(
            module=module,
            action=action,
            performed_by=performed_by,
            target_id=target_id,
            status=status,
            description=description,
            metadata=metadata or {},
        )
        