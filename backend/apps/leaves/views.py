from __future__ import annotations

from rest_framework import status
from rest_framework.views import APIView

from apps.common.permissions import require_role
from apps.common.responses import success, error
from apps.leaves.serializers import LeaveDecisionSerializer, LeaveSerializer
from apps.leaves.services import LeaveService


class LeaveView(APIView):
    """Leave CRUD endpoints.

    POST   /leaves/              -> Apply for leave
    GET    /leaves/              -> List leaves (with filters)
    GET    /leaves/<id>/         -> Get single leave
    PUT    /leaves/<id>/         -> Approve or reject leave (requires reason)

    Note: Delete is intentionally not exposed. Leave records are historical
    business data and must be preserved in MongoDB.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.leave_service = LeaveService()

    @require_role("EMPLOYEE", "HR_MANAGER", "ADMIN", "SUPER_ADMIN")
    def post(self, request):
        """Apply for leave.

        EMPLOYEE role: the employee_id is automatically set from the JWT token.
        Manager roles: can apply on behalf of any active employee.
        """
        data = dict(request.data)
        if request.user.get("role") == "EMPLOYEE":
            data["employee_id"] = str(request.user["_id"])

        serializer = LeaveSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        leave_id = self.leave_service.apply_leave(dict(serializer.validated_data), user_role=request.user.get("role"))

        return success("Leave applied.", {"leave_id": leave_id}, status_code=status.HTTP_201_CREATED)

    @require_role("HR_MANAGER", "ADMIN", "SUPER_ADMIN", "EMPLOYEE")
    def get(self, request, leave_id=None):
        """List leaves or get a single leave."""
        employee_id = request.query_params.get("employee_id")
        status_filter = request.query_params.get("status")
        leave_type = request.query_params.get("leave_type")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))

        if leave_id:
            record = self.leave_service.get_leave(leave_id)
            if request.user.get("role") == "EMPLOYEE" and str(record.get("employee_id")) != str(request.user["_id"]):
                return error("You do not have permission to view this leave.", status_code=status.HTTP_403_FORBIDDEN)
            return success(data=record)

        # Employees can only view their own leaves
        if request.user.get("role") == "EMPLOYEE":
            employee_id = str(request.user["_id"])

        result = self.leave_service.list_leaves(
            employee_id=employee_id,
            status=status_filter,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size,
        )
        return success(data=result)

    @require_role("HR_MANAGER", "ADMIN", "SUPER_ADMIN")
    def put(self, request, leave_id):
        """Approve or reject leave.

        Only PENDING leaves can be approved or rejected.
        The user cannot approve/reject their own leave (enforced in service layer).
        A reason is REQUIRED for both approval and rejection.
        """
        serializer = LeaveDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = dict(serializer.validated_data)

        record = self.leave_service.update_leave_status(
            leave_id,
            validated["status"],
            user_id=str(request.user["_id"]),
            approval_reason=validated.get("approval_reason"),
            rejection_reason=validated.get("rejection_reason"),
        )
        return success(data=record)