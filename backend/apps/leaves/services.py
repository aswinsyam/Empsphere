from __future__ import annotations

import logging
from datetime import datetime
from bson import ObjectId

from django.core.mail import send_mail

from apps.activity_logs.services import log_activity
from apps.common.database import get_collection
from apps.common.constants import Collections
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

logger = logging.getLogger("apps")


class LeaveService:
    """Leave business logic."""

    VALID_STATUSES = {"PENDING", "APPROVED", "REJECTED"}
    VALID_TYPES = {"ANNUAL", "SICK", "CASUAL", "UNPAID"}

    def __init__(self):
        self.collection = get_collection(Collections.LEAVES)
        self.users_collection = get_collection(Collections.USERS)

    def apply_leave(self, data, user_role=None):
        """Apply for leave."""
        employee_id = data.get("employee_id")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        leave_type = data.get("leave_type", "ANNUAL")
        reason = data.get("reason")
        created_by = data.get("created_by")

        if start_date and end_date and start_date > end_date:
            raise ValidationError("Start date cannot be after end date.")
        if leave_type.upper() not in self.VALID_TYPES:
            raise ValidationError(
                f"Invalid leave type. Must be one of: {', '.join(self.VALID_TYPES)}."
            )
        if user_role == "EMPLOYEE" and str(employee_id) != str(created_by):
            raise PermissionDenied("You can only apply for your own leaves.")
        employee = self.users_collection.find_one({"_id": ObjectId(employee_id)})
        if not employee or not employee.get("is_active"):
            raise PermissionDenied("Cannot apply leave for an inactive employee.")

        document = {
            "employee_id": str(employee_id),
            "start_date": str(start_date),
            "end_date": str(end_date),
            "leave_type": leave_type.upper(),
            "reason": reason,
            "status": "PENDING",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "created_by": created_by,
        }
        result = self.collection.insert_one(document)
        leave_id = str(result.inserted_id)
        log_activity(
            module="LEAVE",
            action="APPLY_LEAVE",
            performed_by=str(created_by),
            target_id=leave_id,
            status="SUCCESS",
            description=f"Leave applied for employee {employee_id} from {start_date} to {end_date}.",
        )
        return leave_id

    def get_leave(self, leave_id):
        """Get leave by ID."""
        record = self.collection.find_one({"_id": ObjectId(leave_id)})
        if not record:
            raise NotFound("Leave record not found.")
        return self._serialize(record)

    def list_leaves(self, employee_id=None, status=None, leave_type=None, start_date=None, end_date=None, page=1, page_size=10):
        """List leave records with filters."""
        query = {}
        if employee_id:
            query["employee_id"] = employee_id
        if status:
            query["status"] = status.upper()
        if leave_type:
            query["leave_type"] = leave_type.upper()

        if start_date or end_date:
            if start_date:
                query["end_date"] = {"$gte": start_date}
            if end_date:
                query.setdefault("start_date", {})["$lte"] = end_date

        total_records = self.collection.count_documents(query)
        skip = (page - 1) * page_size
        records = list(
            self.collection.find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(page_size)
        )
        total_pages = (total_records + page_size - 1) // page_size if page_size else 1
        return {
            "leaves": [self._serialize(r) for r in records],
            "total_records": total_records,
            "total_pages": total_pages,
            "page": page,
            "page_size": page_size,
        }

    def update_leave_status(
        self,
        leave_id,
        status,
        user_id,
        approval_reason=None,
        rejection_reason=None,
    ):
        """Approve or reject leave."""
        if status.upper() not in self.VALID_STATUSES:
            raise ValidationError(
                f"Invalid status. Must be one of: {', '.join(self.VALID_STATUSES)}."
            )
        existing = self.collection.find_one({"_id": ObjectId(leave_id)})
        if not existing:
            raise NotFound("Leave record not found.")
        if existing.get("status") != "PENDING":
            raise ValidationError("Only pending leaves can be updated.")
        if str(existing.get("employee_id")) == str(user_id):
            raise PermissionDenied("You cannot approve or reject your own leave.")

        decision = status.upper()
        approval_reason = (approval_reason or "").strip()
        rejection_reason = (rejection_reason or "").strip()
        if decision == "APPROVED" and not approval_reason:
            raise ValidationError({"approval_reason": "Approval reason is required."})
        if decision == "REJECTED" and not rejection_reason:
            raise ValidationError({"rejection_reason": "Rejection reason is required."})

        updates = {
            "status": decision,
            "updated_at": datetime.utcnow(),
            "approval_reason": approval_reason or existing.get("approval_reason", ""),
            "rejection_reason": rejection_reason or existing.get("rejection_reason", ""),
        }
        if decision == "APPROVED":
            updates["approved_by"] = user_id
            updates["rejected_by"] = None
        elif decision == "REJECTED":
            updates["rejected_by"] = user_id
            updates["approved_by"] = None

        self.collection.update_one(
            {"_id": ObjectId(leave_id)}, {"$set": updates}
        )
        record = self.collection.find_one({"_id": ObjectId(leave_id)})
        action = "APPROVE_LEAVE" if decision == "APPROVED" else "REJECT_LEAVE"
        log_activity(
            module="LEAVE",
            action=action,
            performed_by=str(user_id),
            target_id=str(leave_id),
            status="SUCCESS",
            description=f"Leave {decision} for employee {existing.get('employee_id')}.",
        )

        self._send_decision_email(record, decision, approval_reason, rejection_reason)
        return self._serialize(record)

    def _send_decision_email(self, record, decision, approval_reason, rejection_reason):
        """Send the leave decision email to the employee who applied for the leave.

        The recipient email is always looked up from the database (never trusted
        from the frontend). Email failure must NOT fail the DB operation —
        we only log the error and continue.
        """
        employee_id = record.get("employee_id")
        if not employee_id:
            return
        try:
            employee = self.users_collection.find_one({"_id": ObjectId(employee_id)})
        except Exception:
            employee = None
        if not employee:
            logger.warning("Cannot send leave decision email — employee %s not found.", employee_id)
            return
        recipient = employee.get("email")
        if not recipient:
            logger.info("Skipping leave decision email — employee %s has no email.", employee_id)
            return

        first_name = employee.get("first_name", "")
        last_name = employee.get("last_name", "")
        employee_name = (f"{first_name} {last_name}").strip() or "Employee"
        leave_type = record.get("leave_type", "")
        start_date = record.get("start_date", "")
        end_date = record.get("end_date", "")

        if decision == "APPROVED":
            subject = "Your leave request has been approved"
            reason_text = approval_reason or "Your leave request has been approved."
        else:
            subject = "Your leave request has been rejected"
            reason_text = rejection_reason or "Your leave request has been rejected."

        message = (
            f"Hello {employee_name},\n\n"
            f"Your leave request has been {decision.lower()}.\n\n"
            f"Leave Type: {leave_type}\n"
            f"From: {start_date}\n"
            f"To: {end_date}\n"
            f"Status: {decision}\n"
            f"Reason: {reason_text}\n\n"
            f"— EmpSphere"
        )

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=None,
                recipient_list=[recipient],
                fail_silently=True,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to send leave decision email to %s: %s", recipient, exc)

    def _serialize(self, record):
        """Convert a raw MongoDB document into a serialized leave dict."""
        if not record:
            return None
        employee = self.users_collection.find_one({"_id": ObjectId(record.get("employee_id"))}) if record.get("employee_id") else None
        employee_name = None
        employee_code = None
        email = None
        if employee:
            first_name = employee.get("first_name", "")
            last_name = employee.get("last_name", "")
            employee_name = f"{first_name} {last_name}".strip() or None
            employee_code = employee.get("employee_code")
            email = employee.get("email")
        return {
            "leave_id": str(record.get("_id")),
            "employee_id": record.get("employee_id"),
            "employee_name": employee_name,
            "employee_code": employee_code,
            "email": email,
            "start_date": record.get("start_date"),
            "end_date": record.get("end_date"),
            "leave_type": record.get("leave_type"),
            "reason": record.get("reason"),
            "status": record.get("status"),
            "approval_reason": record.get("approval_reason", ""),
            "rejection_reason": record.get("rejection_reason", ""),
            "approved_by": record.get("approved_by"),
            "rejected_by": record.get("rejected_by"),
            "created_at": record.get("created_at"),
            "updated_at": record.get("updated_at"),
        }