"""
Report Service.
Orchestrates report data from existing services and repositories.
"""
from __future__ import annotations

from apps.common.base.base_service import BaseService
from apps.reports.repositories.report_repository import ReportRepository


class ReportService(BaseService):
    """Report business logic."""

    def __init__(self):
        super().__init__()
        self.repository = ReportRepository()
        from apps.employee.services.employee_service import EmployeeService
        from apps.attendance.services.attendance_service import AttendanceService
        from apps.leave.services.leave_service import LeaveService
        self.employee_service = EmployeeService()
        self.attendance_service = AttendanceService()
        self.leave_service = LeaveService()

    def get_employee_report(self, filters):
        """Generate employee report."""
        page = int(filters.get("page", 1))
        page_size = int(filters.get("page_size", 10))
        list_filters = {
            "search": filters.get("search"),
            "department_id": filters.get("department_id"),
            "status": filters.get("status"),
            "page": page,
            "page_size": page_size,
            "joining_date_from": filters.get("joining_date_from"),
            "joining_date_to": filters.get("joining_date_to"),
        }
        summary = self.repository.get_employee_summary(filters)
        result = self.employee_service.list_employees(**list_filters)
        records = result.get("employees", [])
        total_records = result.get("total_records", 0)
        total_pages = result.get("total_pages", 0)
        self.log_activity(
            module="REPORTS",
            action="GENERATE_REPORT",
            performed_by=filters.get("performed_by", ""),
            target_id="",
            status="SUCCESS",
            description="Generated employee report.",
        )
        return {
            "summary": summary,
            "records": records,
            "meta": {
                "page": page,
                "page_size": page_size,
                "total_records": total_records,
                "total_pages": total_pages,
            },
        }

    def get_attendance_report(self, filters):
        """Generate attendance report."""
        page = int(filters.get("page", 1))
        page_size = int(filters.get("page_size", 10))
        list_filters = {
            "employee_id": filters.get("employee_id"),
            "start_date": filters.get("start_date"),
            "end_date": filters.get("end_date"),
            "page": page,
            "page_size": page_size,
        }
        summary = self.repository.get_attendance_summary(filters)
        result = self.attendance_service.list_attendance(**list_filters)
        records = result.get("attendance", [])
        total_records = result.get("total_records", 0)
        total_pages = result.get("total_pages", 0)
        self.log_activity(
            module="REPORTS",
            action="GENERATE_REPORT",
            performed_by=filters.get("performed_by", ""),
            target_id="",
            status="SUCCESS",
            description="Generated attendance report.",
        )
        return {
            "summary": summary,
            "records": records,
            "meta": {
                "page": page,
                "page_size": page_size,
                "total_records": total_records,
                "total_pages": total_pages,
            },
        }

    def get_leave_report(self, filters):
        """Generate leave report."""
        page = int(filters.get("page", 1))
        page_size = int(filters.get("page_size", 10))
        list_filters = {
            "employee_id": filters.get("employee_id"),
            "status": filters.get("status"),
            "leave_type": filters.get("leave_type"),
            "start_date": filters.get("start_date"),
            "end_date": filters.get("end_date"),
            "page": page,
            "page_size": page_size,
        }
        summary = self.repository.get_leave_summary(filters)
        result = self.leave_service.list_leaves(**list_filters)
        records = result.get("leaves", [])
        total_records = result.get("total_records", 0)
        total_pages = result.get("total_pages", 0)
        self.log_activity(
            module="REPORTS",
            action="GENERATE_REPORT",
            performed_by=filters.get("performed_by", ""),
            target_id="",
            status="SUCCESS",
            description="Generated leave report.",
        )
        return {
            "summary": summary,
            "records": records,
            "meta": {
                "page": page,
                "page_size": page_size,
                "total_records": total_records,
                "total_pages": total_pages,
            },
        }

    def get_department_report(self, filters):
        """Generate department report."""
        page = int(filters.get("page", 1))
        page_size = int(filters.get("page_size", 10))
        summary = self.repository.get_department_summary(filters)
        records, total_records, total_pages = self.repository.get_department_report_data(filters)
        self.log_activity(
            module="REPORTS",
            action="GENERATE_REPORT",
            performed_by=filters.get("performed_by", ""),
            target_id="",
            status="SUCCESS",
            description="Generated department report.",
        )
        return {
            "summary": summary,
            "records": records,
            "meta": {
                "page": page,
                "page_size": page_size,
                "total_records": total_records,
                "total_pages": total_pages,
            },
        }

    def get_designation_report(self, filters):
        """Generate designation report."""
        page = int(filters.get("page", 1))
        page_size = int(filters.get("page_size", 10))
        summary = self.repository.get_designation_summary(filters)
        records, total_records, total_pages = self.repository.get_designation_report_data(filters)
        self.log_activity(
            module="REPORTS",
            action="GENERATE_REPORT",
            performed_by=filters.get("performed_by", ""),
            target_id="",
            status="SUCCESS",
            description="Generated designation report.",
        )
        return {
            "summary": summary,
            "records": records,
            "meta": {
                "page": page,
                "page_size": page_size,
                "total_records": total_records,
                "total_pages": total_pages,
            },
        }

    def get_activity_report(self, filters):
        """Generate activity report."""
        page = int(filters.get("page", 1))
        page_size = int(filters.get("page_size", 10))
        summary = self.repository.get_activity_summary(filters)
        query = self.repository._build_activity_query(filters)
        total_records = self.repository.activity_logs.count_documents(query)
        skip = (page - 1) * page_size
        records = list(
            self.repository.activity_logs.find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(page_size)
        )
        total_pages = (total_records + page_size - 1) // page_size if page_size else 1
        serialized = [
            {
                "log_id": str(r.get("_id")),
                "module": r.get("module"),
                "action": r.get("action"),
                "performed_by": r.get("performed_by"),
                "target_id": r.get("target_id"),
                "status": r.get("status"),
                "description": r.get("description"),
                "metadata": r.get("metadata", {}),
                "created_at": r.get("created_at"),
            }
            for r in records
        ]
        self.log_activity(
            module="REPORTS",
            action="GENERATE_REPORT",
            performed_by=filters.get("performed_by", ""),
            target_id="",
            status="SUCCESS",
            description="Generated activity report.",
        )
        return {
            "summary": summary,
            "records": serialized,
            "meta": {
                "page": page,
                "page_size": page_size,
                "total_records": total_records,
                "total_pages": total_pages,
            },
        }
