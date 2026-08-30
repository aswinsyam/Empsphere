"""
Leave Controller.

Exposes RESTful endpoints for leave management.

Why this exists:
- Provides HTTP endpoints for leave operations (apply, list, approve/reject).
- Enforces role-based access control using the @require_role decorator.
- Validates incoming data via serializers before passing to the service layer.
- Enforces employee self-access rules for list and detail views.

Data flow:
HTTP Request → Controller → Serializer validation → Service → Repository → MongoDB
"""
from __future__ import annotations

from rest_framework import status
from rest_framework.views import APIView

from apps.common.base.base_controller import BaseController
from apps.common.decorators.permission import require_role
from apps.common.core.roles import Role
from apps.leave.dtos.leave_dto import LeaveDTO
from apps.leave.serializers.leave_serializer import LeaveSerializer
from apps.leave.services.leave_service import LeaveService


class LeaveController(APIView, BaseController):
    """Leave CRUD endpoints.

    POST   /leaves/              → Apply for leave
    GET    /leaves/              → List leaves (with filters)
    GET    /leaves/<id>/         → Get single leave
    PUT    /leaves/<id>/         → Approve or reject leave

    Note: Delete is intentionally not exposed. Leave records are historical
    business data and must be preserved in MongoDB.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.leave_service = LeaveService()

    @require_role(Role.EMPLOYEE, Role.HR_MANAGER, Role.ADMIN, Role.SUPER_ADMIN)
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

        dto = LeaveDTO(
            **serializer.validated_data,
            created_by=str(request.user["_id"]),
        )

        leave_id = self.leave_service.apply_leave(dto, user_role=request.user.get("role"))

        return self.success(
            message="Leave applied successfully.",
            data={"leave_id": leave_id},
            status_code=status.HTTP_201_CREATED,
        )

    @require_role(Role.HR_MANAGER, Role.ADMIN, Role.SUPER_ADMIN, Role.EMPLOYEE)
    def get(self, request, leave_id=None):
        """List leaves or get a single leave.

        If leave_id is provided, returns that specific leave.
        Otherwise, returns a paginated list filtered by query parameters.

        RBAC:
        - EMPLOYEE: can only view their own leaves.
        - Manager roles: can view any employee's leaves based on query filters.
        """
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
                return self.error(
                    message="You do not have permission to view this leave.",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
            return self.success(
                message="Leave fetched successfully.",
                data=record,
                status_code=status.HTTP_200_OK,
            )

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
        return self.success(
            message="Leaves fetched successfully.",
            data=result,
            status_code=status.HTTP_200_OK,
        )

    @require_role(Role.HR_MANAGER, Role.ADMIN, Role.SUPER_ADMIN)
    def put(self, request, leave_id):
        """Approve or reject leave.

        Only PENDING leaves can be approved or rejected.
        The user cannot approve/reject their own leave (enforced in service layer).
        """
        status_value = request.data.get("status")
        if not status_value:
            return self.error(
                message="Status is required.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        record = self.leave_service.update_leave_status(
            leave_id, status_value, user_id=str(request.user["_id"])
        )
        return self.success(
            message="Leave updated successfully.",
            data=record,
            status_code=status.HTTP_200_OK,
        )
