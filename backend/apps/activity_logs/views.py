"""
Activity log views.

Exposes RESTful endpoints for activity log retrieval.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView

from apps.common.constants import Collections
from apps.common.database import get_collection
from apps.common.permissions import IsAuthenticatedUser, MANAGEABLE_ROLES, require_role
from apps.common.responses import success


class ActivityLogView(APIView):
    """Activity log endpoints."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.collection = get_collection(Collections.ACTIVITY_LOGS)
        self.users_collection = get_collection(Collections.USERS)

    @require_role("HR_MANAGER", "ADMIN", "SUPER_ADMIN", "EMPLOYEE")
    def get(self, request):
        """List activity logs with optional filters."""
        module = request.query_params.get("module")
        action = request.query_params.get("action")
        user_id = request.query_params.get("user_id")
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))

        query = {}
        if module:
            query["module"] = module.upper()
        if action:
            query["action"] = action.upper()

        user_role = request.user.get("role")

        if user_role == "EMPLOYEE":
            query["performed_by"] = str(request.user["_id"])
        elif user_role == "SUPER_ADMIN":
            if user_id:
                query["performed_by"] = user_id
        else:
            manageable_role_names = MANAGEABLE_ROLES.get(user_role, set())
            manageable_user_ids = [
                str(u["_id"])
                for u in self.users_collection.find(
                    {"role": {"$in": list(manageable_role_names)}}
                )
            ]
            if manageable_user_ids:
                query["performed_by"] = {"$in": manageable_user_ids}
            else:
                query["performed_by"] = {"$in": []}
            if user_id and user_id in manageable_user_ids:
                query["performed_by"] = user_id

        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        query.setdefault("created_at", {})["$gte"] = thirty_days_ago

        total_records = self.collection.count_documents(query)
        skip = (page - 1) * page_size
        logs = list(
            self.collection.find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(page_size)
        )

        total_pages = (total_records + page_size - 1) // page_size if page_size else 1

        serialized = []
        for log in logs:
            serialized.append({
                "log_id": str(log.get("_id")),
                "module": log.get("module"),
                "action": log.get("action"),
                "performed_by": log.get("performed_by"),
                "target_id": log.get("target_id"),
                "status": log.get("status"),
                "description": log.get("description"),
                "metadata": log.get("metadata", {}),
                "created_at": log.get("created_at"),
            })

        return success(
            "Activity logs retrieved successfully.",
            data={
                "logs": serialized,
                "meta": {
                    "page": page,
                    "page_size": page_size,
                    "total_records": total_records,
                    "total_pages": total_pages,
                },
            },
            status_code=status.HTTP_200_OK,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticatedUser])
def get_distinct_actions(request):
    """Return distinct action values from activity logs."""
    collection = get_collection(Collections.ACTIVITY_LOGS)
    actions = collection.distinct("action")
    actions = sorted([a for a in actions if a])
    return success(
        "Distinct actions retrieved successfully.",
        data={"actions": actions},
        status_code=status.HTTP_200_OK,
    )
