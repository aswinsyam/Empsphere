"""
Report Repository.
Handles database aggregation and queries for reporting.
"""
from __future__ import annotations

from bson import ObjectId

from apps.common.database.mongo import mongo
from apps.common.core.collections import Collections


class ReportRepository:
    """Report data access layer."""

    def __init__(self):
        self.users = mongo.get_collection(Collections.USERS)
        self.departments = mongo.get_collection(Collections.DEPARTMENTS)
        self.designations = mongo.get_collection(Collections.DESIGNATIONS)
        self.attendance = mongo.get_collection(Collections.ATTENDANCE)
        self.leaves = mongo.get_collection(Collections.LEAVES)
        self.activity_logs = mongo.get_collection(Collections.ACTIVITY_LOGS)

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

    def get_department_report_data(self, filters):
        """Return departments with employee counts."""
        from apps.organization.services.department_service import DepartmentService
        dept_service = DepartmentService()
        page = int(filters.get("page", 1))
        page_size = int(filters.get("page_size", 10))
        result = dept_service.list_departments(
            search=filters.get("search"),
            page=page,
            page_size=page_size,
            include_inactive=filters.get("include_inactive", False),
        )
        departments = result.get("departments", [])
        for dept in departments:
            dept["employee_count"] = dept.get("employee_count", 0)
        return departments, result.get("total_records", 0), result.get("total_pages", 0)

    def get_designation_report_data(self, filters):
        """Return designations with employee counts."""
        from apps.organization.services.designation_service import DesignationService
        desig_service = DesignationService()
        page = int(filters.get("page", 1))
        page_size = int(filters.get("page_size", 10))
        result = desig_service.list_designations(
            search=filters.get("search"),
            page=page,
            page_size=page_size,
            include_inactive=filters.get("include_inactive", False),
        )
        designations = result.get("designations", [])
        for desig in designations:
            desig["employee_count"] = desig.get("employee_count", 0)
        return designations, result.get("total_records", 0), result.get("total_pages", 0)
