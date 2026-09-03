from __future__ import annotations

from datetime import datetime, date
from bson import ObjectId

from apps.activity_logs.services import log_activity
from apps.common.database import get_collection
from apps.common.constants import Collections
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError


class AttendanceService:
    """Attendance business logic."""

    VALID_STATUSES = {"PRESENT", "ABSENT", "HALF_DAY", "LEAVE"}

    def __init__(self):
        self.collection = get_collection(Collections.ATTENDANCE)
        self.users_collection = get_collection(Collections.USERS)
        self._ensure_indexes()

    def _ensure_indexes(self):
        """Create required indexes if they do not exist."""
        existing = {index["name"] for index in self.collection.list_indexes()}
        if "employee_date_unique" not in existing:
            self.collection.create_index(
                [("employee_id", 1), ("date", 1)],
                unique=True,
                name="employee_date_unique",
            )

    def mark_attendance(self, data, user_role=None):
        """Mark attendance for an employee.

        For managers (HR/Admin/SuperAdmin) the operation acts as an "upsert":
        if a record already exists for the same employee + date, it is updated
        with the supplied values. This supports the manual-edit workflow without
        breaking the existing employee-only "mark" flow.
        """
        employee_id = data.get("employee_id")
        date_str = data.get("date")
        status = (data.get("status") or "PRESENT").upper()
        check_in = data.get("check_in")
        check_out = data.get("check_out")
        remarks = data.get("remarks")
        created_by = data.get("created_by")

        if not employee_id:
            raise ValidationError("Employee ID is required.")
        if not date_str:
            raise ValidationError("Date is required.")
        if status not in self.VALID_STATUSES:
            raise ValidationError(
                f"Invalid status. Must be one of: {', '.join(self.VALID_STATUSES)}."
            )
        if user_role == "EMPLOYEE" and str(employee_id) != str(created_by):
            raise PermissionDenied("You can only mark attendance for yourself.")
        employee = self.users_collection.find_one({"_id": ObjectId(employee_id)})
        if not employee or not employee.get("is_active"):
            raise PermissionDenied("Cannot mark attendance for an inactive employee.")

        normalized_date = self._to_date_str(date_str)
        existing = self.collection.find_one({
            "employee_id": str(employee_id),
            "date": normalized_date,
        })

        is_manager = user_role in {"HR_MANAGER", "ADMIN", "SUPER_ADMIN"}

        if existing and not is_manager:
            raise ValidationError("Attendance already marked for this date.")

        if existing and is_manager:
            updates = {
                "status": status,
                "check_in": self._to_datetime(check_in) if check_in else None,
                "check_out": self._to_datetime(check_out) if check_out else None,
                "remarks": remarks,
                "updated_at": datetime.utcnow(),
                "updated_by": created_by,
            }
            self.collection.update_one(
                {"_id": existing["_id"]}, {"$set": updates}
            )
            attendance_id = str(existing["_id"])
            record = self.collection.find_one({"_id": existing["_id"]})
            log_activity(
                module="ATTENDANCE",
                action="UPDATE_ATTENDANCE",
                performed_by=str(created_by),
                target_id=attendance_id,
                status="SUCCESS",
                description=f"Updated attendance for employee {employee_id} on {normalized_date}.",
            )
            return {"attendance_id": attendance_id, "record": self._serialize(record)}

        try:
            document = {
                "employee_id": str(employee_id),
                "date": normalized_date,
                "status": status,
                "check_in": self._to_datetime(check_in) if check_in else None,
                "check_out": self._to_datetime(check_out) if check_out else None,
                "remarks": remarks,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "created_by": created_by,
            }
            result = self.collection.insert_one(document)
            attendance_id = str(result.inserted_id)
            record = self.collection.find_one({"_id": ObjectId(attendance_id)})
        except Exception:
            raise ValidationError("Attendance already marked for this date.")

        log_activity(
            module="ATTENDANCE",
            action="CREATE_ATTENDANCE",
            performed_by=str(created_by),
            target_id=attendance_id,
            status="SUCCESS",
            description=f"Marked attendance for employee {employee_id} on {normalized_date}.",
        )
        return {"attendance_id": attendance_id, "record": self._serialize(record)}

    def check_in(self, employee_id, user_role=None):
        """Check in an employee for today."""
        employee = self.users_collection.find_one({"_id": ObjectId(employee_id)})
        if not employee or not employee.get("is_active"):
            raise PermissionDenied("Cannot check in an inactive employee.")
        today = datetime.utcnow().date().isoformat()
        existing = self.collection.find_one({
            "employee_id": str(employee_id),
            "date": today,
        })
        if existing:
            if existing.get("check_in"):
                raise ValidationError("You have already checked in for today.")
            attendance_id = str(existing["_id"])
            self.collection.update_one(
                {"_id": ObjectId(attendance_id)},
                {"$set": {"check_in": datetime.utcnow(), "updated_at": datetime.utcnow()}},
            )
            record = self.collection.find_one({"_id": ObjectId(attendance_id)})
            log_activity(
                module="ATTENDANCE",
                action="CHECK_IN",
                performed_by=str(employee_id),
                target_id=attendance_id,
                status="SUCCESS",
                description=f"Employee {employee_id} checked in on {today}.",
            )
            return self._serialize(record)
        document = {
            "employee_id": str(employee_id),
            "date": today,
            "status": "PRESENT",
            "check_in": datetime.utcnow(),
            "check_out": None,
            "remarks": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "created_by": str(employee_id),
        }
        result = self.collection.insert_one(document)
        attendance_id = str(result.inserted_id)
        record = self.collection.find_one({"_id": ObjectId(attendance_id)})
        log_activity(
            module="ATTENDANCE",
            action="CHECK_IN",
            performed_by=str(employee_id),
            target_id=attendance_id,
            status="SUCCESS",
            description=f"Employee {employee_id} checked in on {today}.",
        )
        return self._serialize(record)

    def check_out(self, employee_id, user_role=None):
        """Check out an employee for today."""
        employee = self.users_collection.find_one({"_id": ObjectId(employee_id)})
        if not employee or not employee.get("is_active"):
            raise PermissionDenied("Cannot check out an inactive employee.")
        today = datetime.utcnow().date().isoformat()
        existing = self.collection.find_one({
            "employee_id": str(employee_id),
            "date": today,
        })
        if not existing:
            raise NotFound("You have not checked in for today.")
        if not existing.get("check_in"):
            raise PermissionDenied("You must check in before checking out.")
        if existing.get("check_out"):
            raise ValidationError("You have already checked out for today.")
        attendance_id = str(existing["_id"])
        self.collection.update_one(
            {"_id": ObjectId(attendance_id)},
            {"$set": {"check_out": datetime.utcnow(), "updated_at": datetime.utcnow()}},
        )
        record = self.collection.find_one({"_id": ObjectId(attendance_id)})
        log_activity(
            module="ATTENDANCE",
            action="CHECK_OUT",
            performed_by=str(employee_id),
            target_id=attendance_id,
            status="SUCCESS",
            description=f"Employee {employee_id} checked out on {today}.",
        )
        return self._serialize(record)

    def get_attendance(self, attendance_id):
        """Get attendance by ID."""
        record = self.collection.find_one({"_id": ObjectId(attendance_id)})
        if not record:
            raise NotFound("Attendance record not found.")
        return self._serialize(record)

    def list_attendance(self, employee_id=None, start_date=None, end_date=None, status=None, page=1, page_size=10):
        """List attendance records with filters."""
        query = {}
        if employee_id:
            query["employee_id"] = employee_id
        if status:
            query["status"] = status.upper()
        if start_date:
            query["date"] = {"$gte": start_date}
        if end_date:
            query.setdefault("date", {})["$lte"] = end_date

        total_records = self.collection.count_documents(query)
        skip = (page - 1) * page_size
        records = list(
            self.collection.find(query)
            .sort("date", -1)
            .skip(skip)
            .limit(page_size)
        )
        total_pages = (total_records + page_size - 1) // page_size if page_size else 1
        return {
            "attendance": [self._serialize(r) for r in records],
            "total_records": total_records,
            "total_pages": total_pages,
            "page": page,
            "page_size": page_size,
        }

    def update_attendance(self, attendance_id, data, user_role=None, actor_id=None):
        """Update attendance.

        Behaviour:
          * If ``attendance_id`` is a valid ObjectId and the record exists,
            that record is updated.
          * Otherwise (or when the record does not exist), look up by
            ``employee_id`` + ``date`` from the payload and upsert. This lets
            a manager submit an "edit" payload even when there was no
            attendance record yet, which is the manual mark workflow.
        """
        data = dict(data or {})
        existing = None
        if attendance_id and ObjectId.is_valid(attendance_id):
            existing = self.collection.find_one({"_id": ObjectId(attendance_id)})

        if not existing:
            employee_id = data.get("employee_id")
            date_str = data.get("date")
            if employee_id and date_str:
                normalized_date = self._to_date_str(date_str)
                existing = self.collection.find_one({
                    "employee_id": str(employee_id),
                    "date": normalized_date,
                })

        if not existing:
            raise NotFound("Attendance record not found.")

        updates = {}
        if data.get("status"):
            if data["status"].upper() not in self.VALID_STATUSES:
                raise ValidationError(
                    f"Invalid status. Must be one of: {', '.join(self.VALID_STATUSES)}."
                )
            updates["status"] = data["status"].upper()
        if data.get("check_in") is not None:
            updates["check_in"] = self._to_datetime(data["check_in"]) if data["check_in"] else None
        if data.get("check_out") is not None:
            updates["check_out"] = self._to_datetime(data["check_out"]) if data["check_out"] else None
        if data.get("remarks") is not None:
            updates["remarks"] = data["remarks"]
        if not updates:
            return self._serialize(existing)

        updates["updated_at"] = datetime.utcnow()
        if actor_id:
            updates["updated_by"] = actor_id

        self.collection.update_one(
            {"_id": existing["_id"]}, {"$set": updates}
        )
        record = self.collection.find_one({"_id": existing["_id"]})
        log_activity(
            module="ATTENDANCE",
            action="UPDATE_ATTENDANCE",
            performed_by=str(actor_id) if actor_id else None,
            target_id=str(existing["_id"]),
            status="SUCCESS",
            description=f"Updated attendance for employee {existing.get('employee_id')} on {existing.get('date')}.",
        )
        return self._serialize(record)

    def get_attendance_summary(self, employee_id, start_date=None, end_date=None):
        """Get attendance summary for an employee."""
        query = {"employee_id": employee_id}
        if start_date:
            query["date"] = {"$gte": start_date}
        if end_date:
            query.setdefault("date", {})["$lte"] = end_date

        records = list(self.collection.find(query))
        summary = {
            "total_days": len(records),
            "present_days": sum(1 for r in records if r.get("status") == "PRESENT"),
            "absent_days": sum(1 for r in records if r.get("status") == "ABSENT"),
            "half_days": sum(1 for r in records if r.get("status") == "HALF_DAY"),
            "leave_days": sum(1 for r in records if r.get("status") == "LEAVE"),
        }
        summary["attendance_percentage"] = (
            round((summary["present_days"] / summary["total_days"]) * 100, 2)
            if summary["total_days"] > 0
            else 0
        )
        return summary

    def _to_datetime(self, value):
        """Convert a date or datetime to a datetime object."""
        if isinstance(value, datetime):
            return value
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time())
        return value

    def _to_date_str(self, value):
        """Convert a date or datetime to a date string."""
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        return str(value)

    def _serialize(self, record):
        """Convert a raw MongoDB document into a serialized attendance dict."""
        if not record:
            return None
        return {
            "attendance_id": str(record.get("_id")),
            "employee_id": record.get("employee_id"),
            "date": record.get("date"),
            "status": record.get("status"),
            "check_in": record.get("check_in"),
            "check_out": record.get("check_out"),
            "remarks": record.get("remarks"),
            "created_at": record.get("created_at"),
            "updated_at": record.get("updated_at"),
        }
