from __future__ import annotations

from rest_framework import status
from rest_framework.views import APIView

from apps.common.permissions import require_role
from apps.common.responses import success, error
from apps.reports.services import ReportService


class ReportView(APIView):
    """Report endpoints."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.report_service = ReportService()

    @require_role("SUPER_ADMIN", "ADMIN", "HR_MANAGER")
    def get(self, request):
        """Dispatch report requests based on the URL path."""
        path = request.path.rstrip("/")
        report_type = path.rsplit("/", 1)[-1]

        filters = {
            "performed_by": str(request.user.get("_id", "")),
            "actor_role": request.user.get("role"),
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
            return success("Employee report generated.", data)

        if report_type == "attendance":
            filters.update({
                "employee_id": request.query_params.get("employee_id"),
                "department_id": request.query_params.get("department_id"),
                "start_date": request.query_params.get("start_date"),
                "end_date": request.query_params.get("end_date"),
                "status": request.query_params.get("status"),
            })
            data = self.report_service.get_attendance_report(filters)
            return success("Attendance report generated.", data)

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
            return success("Leave report generated.", data)

        if report_type == "departments":
            filters.update({
                "search": request.query_params.get("search"),
                "include_inactive": request.query_params.get("include_inactive", "false").lower() == "true",
            })
            data = self.report_service.get_department_report(filters)
            return success("Department report generated.", data)

        if report_type == "designations":
            filters.update({
                "search": request.query_params.get("search"),
                "include_inactive": request.query_params.get("include_inactive", "false").lower() == "true",
            })
            data = self.report_service.get_designation_report(filters)
            return success("Designation report generated.", data)

        if report_type == "activity":
            filters.update({
                "module": request.query_params.get("module"),
                "action": request.query_params.get("action"),
                "user_id": request.query_params.get("user_id"),
                "start_date": request.query_params.get("start_date"),
                "end_date": request.query_params.get("end_date"),
            })
            data = self.report_service.get_activity_report(filters)
            return success("Activity report generated.", data)

        return error("Unknown report type.", status.HTTP_400_BAD_REQUEST)
