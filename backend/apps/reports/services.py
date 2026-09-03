from __future__ import annotations

from apps.activity_logs.services import log_activity
from apps.common.database import get_collection
from apps.common.constants import Collections
from apps.employees.services import EmployeeService
from apps.attendance.services import AttendanceService
from apps.leaves.services import LeaveService
from apps.departments.services import DepartmentService
from apps.designations.services import DesignationService


class ReportService:
    """Report business logic."""

    def __init__(self):
        self.users = get_collection(Collections.USERS)
        self.departments = get_collection(Collections.DEPARTMENTS)
        self.designations = get_collection(Collections.DESIGNATIONS)
        self.attendance = get_collection(Collections.ATTENDANCE)
        self.leaves = get_collection(Collections.LEAVES)
        self.activity_logs = get_collection(Collections.ACTIVITY_LOGS)
        self.employee_service = EmployeeService()
        self.attendance_service = AttendanceService()
        self.leave_service = LeaveService()
        self.department_service = DepartmentService()
        self.designation_service = DesignationService()

    def _build_employee_query(self, filters):
        """Build MongoDB query for employee reports from filter dict."""
        query = {}
        if filters.get("department_id"):
            query["department_id"] = filters["department_id"]
        if filters.get("designation_id"):
            query["designation_id"] = filters["designation_id"]
        if filters.get("status"):
            query["status"] = filters["status"].upper()
        if filters.get("joining_date_from"):
            query["joining_date"] = {"$gte": filters["joining_date_from"]}
        if filters.get("joining_date_to"):
            query.setdefault("joining_date", {})["$lte"] = filters["joining_date_to"]
        return query

    def get_employee_summary(self, filters):
        """Return employee summary stats for the given filters."""
        query = self._build_employee_query(filters)
        total = self.users.count_documents(query)
        active = self.users.count_documents({**query, "status": "ACTIVE"})
        inactive = self.users.count_documents({**query, "status": "INACTIVE"})

        by_department = self._group_employees_by_department(query)
        by_designation = self._group_employees_by_designation(query)
        by_role = self._group_employees_by_role(query)

        return {
            "total": total,
            "active": active,
            "inactive": inactive,
            "by_department": by_department,
            "by_designation": by_designation,
            "by_role": by_role,
        }

    def _group_employees_by_department(self, query):
        """Group employee counts by department."""
        from bson import ObjectId
        pipeline = [
            {"$match": query},
            {"$group": {"_id": "$department_id", "count": {"$sum": 1}}},
        ]
        groups = list(self.users.aggregate(pipeline))
        dept_ids = [g["_id"] for g in groups if g.get("_id")]
        dept_map = {}
        if dept_ids:
            object_ids = [ObjectId(d) for d in dept_ids if ObjectId.is_valid(d)]
            if object_ids:
                for dept in self.departments.find({"_id": {"$in": object_ids}}):
                    dept_map[str(dept["_id"])] = dept.get("name", "Unknown")
        return [
            {
                "department_id": g["_id"],
                "department_name": dept_map.get(g["_id"], "No Department") if g.get("_id") else "No Department",
                "count": g["count"],
            }
            for g in groups
        ]

    def _group_employees_by_designation(self, query):
        """Group employee counts by designation."""
        from bson import ObjectId
        pipeline = [
            {"$match": query},
            {"$group": {"_id": "$designation_id", "count": {"$sum": 1}}},
        ]
        groups = list(self.users.aggregate(pipeline))
        desig_ids = [g["_id"] for g in groups if g.get("_id")]
        desig_map = {}
        if desig_ids:
            object_ids = [d for d in desig_ids if ObjectId.is_valid(d)]
            if object_ids:
                for desig in self.designations.find({"_id": {"$in": object_ids}}):
                    desig_map[str(desig["_id"])] = desig.get("name", "Unknown")
        return [
            {
                "designation_id": g["_id"],
                "designation_name": desig_map.get(g["_id"], "No Designation") if g.get("_id") else "No Designation",
                "count": g["count"],
            }
            for g in groups
        ]

    def _group_employees_by_role(self, query):
        """Group employee counts by role."""
        pipeline = [
            {"$match": query},
            {"$group": {"_id": "$role", "count": {"$sum": 1}}},
        ]
        groups = list(self.users.aggregate(pipeline))
        return [
            {
                "role": g.get("_id") or "Unknown",
                "count": g["count"],
            }
            for g in groups
        ]

    def get_attendance_summary(self, filters):
        """Return attendance summary stats for the given filters."""
        query = self._build_attendance_query(filters)
        total = self.attendance.count_documents(query)
        present = self.attendance.count_documents({**query, "status": "PRESENT"})
        absent = self.attendance.count_documents({**query, "status": "ABSENT"})
        half_day = self.attendance.count_documents({**query, "status": "HALF_DAY"})
        leave = self.attendance.count_documents({**query, "status": "LEAVE"})
        return {
            "total": total,
            "present": present,
            "absent": absent,
            "half_day": half_day,
            "leave": leave,
        }

    def _build_attendance_query(self, filters):
        """Build MongoDB query for attendance reports."""
        query = {}
        if filters.get("employee_id"):
            query["employee_id"] = filters["employee_id"]
        if filters.get("start_date"):
            query["date"] = {"$gte": filters["start_date"]}
        if filters.get("end_date"):
            query.setdefault("date", {})["$lte"] = filters["end_date"]
        if filters.get("status"):
            query["status"] = filters["status"].upper()
        if filters.get("department_id"):
            employees = list(self.users.find({"department_id": filters["department_id"]}, {"_id": 1}))
            emp_ids = [str(e["_id"]) for e in employees]
            query["employee_id"] = {"$in": emp_ids}
        return query

    def get_leave_summary(self, filters):
        """Return leave summary stats for the given filters."""
        query = self._build_leave_query(filters)
        total = self.leaves.count_documents(query)
        pending = self.leaves.count_documents({**query, "status": "PENDING"})
        approved = self.leaves.count_documents({**query, "status": "APPROVED"})
        rejected = self.leaves.count_documents({**query, "status": "REJECTED"})
        by_type = self._group_leaves_by_type(query)
        return {
            "total": total,
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
            "by_type": by_type,
        }

    def _build_leave_query(self, filters):
        """Build MongoDB query for leave reports."""
        query = {}
        if filters.get("employee_id"):
            query["employee_id"] = filters["employee_id"]
        if filters.get("status"):
            query["status"] = filters["status"].upper()
        if filters.get("leave_type"):
            query["leave_type"] = filters["leave_type"].upper()
        date_query = {}
        if filters.get("start_date"):
            date_query["$gte"] = filters["start_date"]
        if filters.get("end_date"):
            date_query["$lte"] = filters["end_date"]
        if date_query:
            query["start_date"] = date_query
        if filters.get("department_id"):
            employees = list(self.users.find({"department_id": filters["department_id"]}, {"_id": 1}))
            emp_ids = [str(e["_id"]) for e in employees]
            query["employee_id"] = {"$in": emp_ids}
        return query

    def _group_leaves_by_type(self, query):
        """Group leave counts by leave type."""
        pipeline = [
            {"$match": query},
            {"$group": {"_id": "$leave_type", "count": {"$sum": 1}}},
        ]
        groups = list(self.leaves.aggregate(pipeline))
        return [
            {
                "leave_type": g.get("_id") or "Unknown",
                "count": g["count"],
            }
            for g in groups
        ]

    def get_department_summary(self, filters):
        """Return department summary stats."""
        query = {}
        if not filters.get("include_inactive"):
            query["is_active"] = True
        if filters.get("search"):
            query["$or"] = [
                {"name": {"$regex": filters["search"], "$options": "i"}},
                {"code": {"$regex": filters["search"], "$options": "i"}},
            ]
        total = self.departments.count_documents(query)
        active = self.departments.count_documents({**query, "is_active": True})
        inactive = self.departments.count_documents({**query, "is_active": False})
        return {
            "total": total,
            "active": active,
            "inactive": inactive,
        }

    def get_designation_summary(self, filters):
        """Return designation summary stats."""
        query = {}
        if not filters.get("include_inactive"):
            query["is_active"] = True
        if filters.get("search"):
            query["$or"] = [
                {"name": {"$regex": filters["search"], "$options": "i"}},
                {"code": {"$regex": filters["search"], "$options": "i"}},
            ]
        total = self.designations.count_documents(query)
        active = self.designations.count_documents({**query, "is_active": True})
        inactive = self.designations.count_documents({**query, "is_active": False})
        return {
            "total": total,
            "active": active,
            "inactive": inactive,
        }

    def get_activity_summary(self, filters):
        """Return activity log summary stats."""
        query = self._build_activity_query(filters)
        total = self.activity_logs.count_documents(query)
        by_action = self._group_activities_by_action(query)
        by_module = self._group_activities_by_module(query)
        return {
            "total": total,
            "by_action": by_action,
            "by_module": by_module,
        }

    def _build_activity_query(self, filters):
        """Build MongoDB query for activity reports."""
        query = {}
        if filters.get("module"):
            query["module"] = filters["module"].upper()
        if filters.get("action"):
            query["action"] = filters["action"].upper()
        if filters.get("user_id"):
            query["performed_by"] = filters["user_id"]
        if filters.get("start_date"):
            query["created_at"] = {"$gte": filters["start_date"]}
        if filters.get("end_date"):
            query.setdefault("created_at", {})["$lte"] = filters["end_date"]
        return query

    def _group_activities_by_action(self, query):
        """Group activity counts by action."""
        pipeline = [
            {"$match": query},
            {"$group": {"_id": "$action", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]
        groups = list(self.activity_logs.aggregate(pipeline))
        return [{"action": g.get("_id") or "Unknown", "count": g["count"]} for g in groups]

    def _group_activities_by_module(self, query):
        """Group activity counts by module."""
        pipeline = [
            {"$match": query},
            {"$group": {"_id": "$module", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]
        groups = list(self.activity_logs.aggregate(pipeline))
        return [{"module": g.get("_id") or "Unknown", "count": g["count"]} for g in groups]

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
            "actor_role": filters.get("actor_role"),
        }
        summary = self.get_employee_summary(filters)
        result = self.employee_service.list_employees(**list_filters)
        records = result.get("employees", [])
        total_records = result.get("total_records", 0)
        total_pages = result.get("total_pages", 0)
        log_activity(
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
        summary = self.get_attendance_summary(filters)
        result = self.attendance_service.list_attendance(**list_filters)
        records = result.get("attendance", [])
        total_records = result.get("total_records", 0)
        total_pages = result.get("total_pages", 0)
        log_activity(
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
        summary = self.get_leave_summary(filters)
        result = self.leave_service.list_leaves(**list_filters)
        records = result.get("leaves", [])
        total_records = result.get("total_records", 0)
        total_pages = result.get("total_pages", 0)
        log_activity(
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
        summary = self.get_department_summary(filters)
        records, total_records, total_pages = self._get_department_report_data(filters)
        log_activity(
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
        summary = self.get_designation_summary(filters)
        records, total_records, total_pages = self._get_designation_report_data(filters)
        log_activity(
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
        summary = self.get_activity_summary(filters)
        query = self._build_activity_query(filters)
        total_records = self.activity_logs.count_documents(query)
        skip = (page - 1) * page_size
        records = list(
            self.activity_logs.find(query)
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
        log_activity(
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

    def _get_department_report_data(self, filters):
        """Return departments with employee counts."""
        page = int(filters.get("page", 1))
        page_size = int(filters.get("page_size", 10))
        result = self.department_service.list_departments(
            search=filters.get("search"),
            page=page,
            page_size=page_size,
            include_inactive=filters.get("include_inactive", False),
        )
        departments = result.get("departments", [])
        for dept in departments:
            dept["employee_count"] = dept.get("employee_count", 0)
        return departments, result.get("total_records", 0), result.get("total_pages", 0)

    def _get_designation_report_data(self, filters):
        """Return designations with employee counts."""
        page = int(filters.get("page", 1))
        page_size = int(filters.get("page_size", 10))
        result = self.designation_service.list_designations(
            search=filters.get("search"),
            page=page,
            page_size=page_size,
            include_inactive=filters.get("include_inactive", False),
        )
        designations = result.get("designations", [])
        for desig in designations:
            desig["employee_count"] = desig.get("employee_count", 0)
        return designations, result.get("total_records", 0), result.get("total_pages", 0)
