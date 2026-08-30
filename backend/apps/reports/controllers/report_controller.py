"""
Report Controller.
Exposes centralized reporting endpoints for management users.
"""
from __future__ import annotations

from rest_framework import status
from rest_framework.views import APIView

from apps.common.base.base_controller import BaseController
from apps.common.decorators.permission import require_role
from apps.common.core.roles import EMPLOYEE_MANAGER_ROLES
from apps.reports.services.report_service import ReportService


class ReportController(APIView, BaseController):
    """Report endpoints."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.report_service = ReportService()

    @require_role(*EMPLOYEE_MANAGER_ROLES)
    def get(self, request):
        """Dispatch report requests based on the URL path."""
        path = request.path.rstrip("/")
        report_type = path.rsplit("/", 1)[-1]

        filters = {
            "performed_by": str(request.user.get("_id", "")),
            "search": request.query_params.get("search"),
            "page": request.query_params.get("page", 1),
            "page_size": request.query_params.get("page_size", 10),
        }

        if report_type == "employees":
            filters.update({
                "department_id": request.query_params.get("department_id"),
                "designation_id": request.query_params.get("designation_id"),
                "status": request.query_params.get("status"),
                "joining_date_from": request.query_params.get("joining_date_from"),
                "joining_date_to": request.query_params.get("joining_date_to"),
            })
            data = self.report_service.get_employee_report(filters)
            return self.success(
                message="Employee report generated successfully.",
                data=data,
                status_code=status.HTTP_200_OK,
            )

        if report_type == "attendance":
            filters.update({
                "employee_id": request.query_params.get("employee_id"),
                "department_id": request.query_params.get("department_id"),
                "start_date": request.query_params.get("start_date"),
                "end_date": request.query_params.get("end_date"),
                "status": request.query_params.get("status"),
            })
            data = self.report_service.get_attendance_report(filters)
            return self.success(
                message="Attendance report generated successfully.",
                data=data,
                status_code=status.HTTP_200_OK,
            )

        if report_type == "leaves":
            filters.update({
                "employee_id": request.query_params.get("employee_id"),
                "department_id": request.query_params.get("department_id"),
                "start_date": request.query_params.get("start_date"),
                "end_date": request.query_params.get("end_date"),
                "status": request.query_params.get("status"),
                "leave_type": request.query_params.get("leave_type"),
            })
            data = self.report_service.get_leave_report(filters)
            return self.success(
                message="Leave report generated successfully.",
                data=data,
                status_code=status.HTTP_200_OK,
            )

        if report_type == "departments":
            filters.update({
                "search": request.query_params.get("search"),
                "include_inactive": request.query_params.get("include_inactive", "false").lower() == "true",
            })
            data = self.report_service.get_department_report(filters)
            return self.success(
                message="Department report generated successfully.",
                data=data,
                status_code=status.HTTP_200_OK,
            )

        if report_type == "designations":
            filters.update({
                "search": request.query_params.get("search"),
                "include_inactive": request.query_params.get("include_inactive", "false").lower() == "true",
            })
            data = self.report_service.get_designation_report(filters)
            return self.success(
                message="Designation report generated successfully.",
                data=data,
                status_code=status.HTTP_200_OK,
            )

        if report_type == "activity":
            filters.update({
                "module": request.query_params.get("module"),
                "action": request.query_params.get("action"),
                "user_id": request.query_params.get("user_id"),
                "start_date": request.query_params.get("start_date"),
                "end_date": request.query_params.get("end_date"),
            })
            data = self.report_service.get_activity_report(filters)
            return self.success(
                message="Activity report generated successfully.",
                data=data,
                status_code=status.HTTP_200_OK,
            )

        return self.error(
            message="Unknown report type.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
