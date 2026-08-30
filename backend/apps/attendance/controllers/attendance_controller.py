"""
Attendance Controller.

Exposes RESTful endpoints for attendance management.
"""
from __future__ import annotations

from rest_framework import status
from rest_framework.views import APIView

from apps.common.base.base_controller import BaseController
from apps.common.decorators.permission import require_role
from apps.common.core.roles import Role
from apps.attendance.dtos.attendance_dto import AttendanceDTO, AttendanceUpdateDTO
from apps.attendance.serializers.attendance_serializer import (
    AttendanceSerializer,
    AttendanceUpdateSerializer,
    CheckInSerializer,
    CheckOutSerializer,
)
from apps.attendance.services.attendance_service import AttendanceService


class AttendanceController(APIView, BaseController):
    """Attendance CRUD endpoints."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.attendance_service = AttendanceService()

    @require_role(Role.EMPLOYEE, Role.HR_MANAGER, Role.ADMIN, Role.SUPER_ADMIN)
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

        dto = AttendanceDTO(
            **serializer.validated_data,
            created_by=str(request.user["_id"]),
        )

        attendance_id = self.attendance_service.mark_attendance(dto, user_role=request.user.get("role"))

        return self.success(
            message="Attendance marked successfully.",
            data={"attendance_id": attendance_id},
            status_code=status.HTTP_201_CREATED,
        )

    def _check_in(self, request):
        """Check in the current user for today."""
        serializer = CheckInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee_id = str(request.user["_id"])
        record = self.attendance_service.check_in(employee_id, user_role=request.user.get("role"))
        return self.success(
            message="Checked in successfully.",
            data=record,
            status_code=status.HTTP_200_OK,
        )

    def _check_out(self, request):
        """Check out the current user for today."""
        serializer = CheckOutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee_id = str(request.user["_id"])
        record = self.attendance_service.check_out(employee_id, user_role=request.user.get("role"))
        return self.success(
            message="Checked out successfully.",
            data=record,
            status_code=status.HTTP_200_OK,
        )

    @require_role(Role.HR_MANAGER, Role.ADMIN, Role.SUPER_ADMIN, Role.EMPLOYEE)
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
                return self.error(
                    message="You do not have permission to view this attendance record.",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
            return self.success(
                message="Attendance fetched successfully.",
                data=record,
                status_code=status.HTTP_200_OK,
            )

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
        return self.success(
            message="Attendance fetched successfully.",
            data=result,
            status_code=status.HTTP_200_OK,
        )

    @require_role(Role.HR_MANAGER, Role.ADMIN, Role.SUPER_ADMIN)
    def put(self, request, attendance_id):
        """Update attendance."""
        serializer = AttendanceUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dto = AttendanceUpdateDTO(
            **serializer.validated_data,
            updated_by=str(request.user["_id"]),
        )

        record = self.attendance_service.update_attendance(
            attendance_id, dto, user_role=request.user.get("role")
        )

        return self.success(
            message="Attendance updated successfully.",
            data=record,
            status_code=status.HTTP_200_OK,
        )


class AttendanceSummaryController(APIView, BaseController):
    """Attendance summary endpoint."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.attendance_service = AttendanceService()

    @require_role(Role.HR_MANAGER, Role.ADMIN, Role.SUPER_ADMIN, Role.EMPLOYEE)
    def get(self, request, employee_id):
        """Get attendance summary for an employee."""
        # Employees can only view their own summary
        if request.user.get("role") == "EMPLOYEE":
            if str(request.user["_id"]) != employee_id:
                return self.error(
                    message="You do not have permission to view this summary.",
                    status_code=status.HTTP_403_FORBIDDEN,
                )

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        summary = self.attendance_service.get_attendance_summary(
            employee_id, start_date=start_date, end_date=end_date
        )
        return self.success(
            message="Attendance summary fetched successfully.",
            data=summary,
            status_code=status.HTTP_200_OK,
        )
