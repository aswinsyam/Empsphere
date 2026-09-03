from __future__ import annotations

from rest_framework import status
from rest_framework.views import APIView

from apps.common.permissions import require_role
from apps.common.responses import success, error
from apps.attendance.serializers import (
    AttendanceSerializer,
    AttendanceUpdateSerializer,
    CheckInSerializer,
    CheckOutSerializer,
)
from apps.attendance.services import AttendanceService


class AttendanceView(APIView):
    """Attendance CRUD endpoints."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.attendance_service = AttendanceService()

    @require_role("EMPLOYEE", "HR_MANAGER", "ADMIN", "SUPER_ADMIN")
    def post(self, request, action=None):
        """Handle attendance actions: mark, check-in, check-out."""
        if action == "check-in":
            return self._check_in(request)
        if action == "check-out":
            return self._check_out(request)
        return self._mark_attendance(request)

    def _mark_attendance(self, request):
        """Mark attendance for an employee."""
        data = dict(request.data)
        if request.user.get("role") == "EMPLOYEE":
            data["employee_id"] = str(request.user["_id"])

        serializer = AttendanceSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        attendance_id = self.attendance_service.mark_attendance(dict(serializer.validated_data), user_role=request.user.get("role"))

        return success("Attendance marked.", {"attendance_id": attendance_id}, status.HTTP_201_CREATED)

    def _check_in(self, request):
        """Check in the current user for today."""
        serializer = CheckInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee_id = str(request.user["_id"])
        record = self.attendance_service.check_in(employee_id, user_role=request.user.get("role"))
        return success("Checked in.", record)

    def _check_out(self, request):
        """Check out the current user for today."""
        serializer = CheckOutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee_id = str(request.user["_id"])
        record = self.attendance_service.check_out(employee_id, user_role=request.user.get("role"))
        return success("Checked out.", record)

    @require_role("HR_MANAGER", "ADMIN", "SUPER_ADMIN", "EMPLOYEE")
    def get(self, request, attendance_id=None):
        """List attendance records or get a single record."""
        employee_id = request.query_params.get("employee_id")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        status_filter = request.query_params.get("status")
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))

        if attendance_id:
            record = self.attendance_service.get_attendance(attendance_id)
            if request.user.get("role") == "EMPLOYEE" and str(record.get("employee_id")) != str(request.user["_id"]):
                return error("You do not have permission to view this attendance record.", status.HTTP_403_FORBIDDEN)
            return success("Attendance record retrieved.", record)

        # Employees can only view their own attendance
        if request.user.get("role") == "EMPLOYEE":
            employee_id = str(request.user["_id"])

        result = self.attendance_service.list_attendance(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            status=status_filter,
            page=page,
            page_size=page_size,
        )
        return success("Attendance records retrieved.", result)

    @require_role("HR_MANAGER", "ADMIN", "SUPER_ADMIN")
    def put(self, request, attendance_id):
        """Update attendance.

        Supports two modes:
          1. ``attendance_id`` (from the existing row in the table) — updates
             that record directly.
          2. If the id is not a valid ObjectId or the record does not exist,
             we look up by ``employee_id`` + ``date`` from the payload and
             upsert. This means an HR/Admin can submit an edit even when
             there was no prior record (manual mark).
        """
        data = dict(request.data)
        data["updated_by"] = str(request.user["_id"])
        serializer = AttendanceUpdateSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        record = self.attendance_service.update_attendance(
            attendance_id,
            dict(serializer.validated_data),
            user_role=request.user.get("role"),
            actor_id=str(request.user["_id"]),
        )

        return success("Attendance updated.", record)


class AttendanceSummaryView(APIView):
    """Attendance summary endpoint."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.attendance_service = AttendanceService()

    @require_role("HR_MANAGER", "ADMIN", "SUPER_ADMIN", "EMPLOYEE")
    def get(self, request, employee_id):
        """Get attendance summary for an employee."""
        # Employees can only view their own summary
        if request.user.get("role") == "EMPLOYEE":
            if str(request.user["_id"]) != employee_id:
                return error("You do not have permission to view this summary.", status.HTTP_403_FORBIDDEN)

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        summary = self.attendance_service.get_attendance_summary(
            employee_id, start_date=start_date, end_date=end_date
        )
        return success("Attendance summary retrieved.", summary)
