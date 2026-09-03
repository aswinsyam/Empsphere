from __future__ import annotations

import re
import time
import uuid
from datetime import datetime, timedelta
from bson import ObjectId

from apps.activity_logs.services import log_activity
from apps.common.database import get_collection
from apps.common.constants import Collections
from apps.common.settings import settings
from apps.payments.gateways import razorpay_gateway
from rest_framework.exceptions import (
    PermissionDenied,
    NotFound,
    ValidationError,
)


class AmenityService:
    """Office amenity business logic and orchestration."""

    def __init__(self):
        self.collection = get_collection(Collections.AMENITIES)
        self._ensure_indexes()

    def _ensure_indexes(self):
        """Create required indexes if they do not exist."""
        existing = {index["name"] for index in self.collection.list_indexes()}
        if "amenity_name_unique" not in existing:
            self.collection.create_index(
                [("name", 1)],
                unique=True,
                name="amenity_name_unique",
            )

    def create_amenity(self, data):
        """Create a new amenity after validating input."""
        name = (data.get("name") or "").strip()
        description = data.get("description") or ""
        amount = data.get("amount")
        created_by = data.get("created_by")

        if not name:
            raise ValidationError("Amenity name is required.")
        if amount is None or float(amount) <= 0:
            raise ValidationError("Amount must be a positive number.")

        existing = self.collection.find_one({"name": {"$regex": f"^{re.escape(name)}$", "$options": "i"}})
        if existing:
            raise ValidationError("An amenity with this name already exists.")

        document = {
            "name": name,
            "description": description,
            "amount": float(amount),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "created_by": created_by,
        }
        amenity_id = str(self.collection.insert_one(document).inserted_id)

        log_activity(
            module="AMENITY",
            action="AMENITY_CREATED",
            performed_by=str(created_by),
            target_id=amenity_id,
            status="SUCCESS",
            description=f"Created amenity: {name} (₹{amount}).",
        )
        return self._serialize(self.collection.find_one({"_id": ObjectId(amenity_id)}))

    def get_active_amenity(self, amenity_id: str) -> dict:
        """Get an active amenity by ID."""
        if not ObjectId.is_valid(amenity_id):
            raise NotFound("Amenity not found or inactive.")
        amenity = self.collection.find_one({"_id": ObjectId(amenity_id)})
        if not amenity or not amenity.get("is_active"):
            raise NotFound("Amenity not found or inactive.")
        return self._serialize(amenity)

    def list_amenities(self, include_inactive: bool = False) -> list[dict]:
        """List all amenities."""
        query = {}
        if not include_inactive:
            query["is_active"] = True
        records = list(self.collection.find(query))
        return [self._serialize(a) for a in records]

    def update_amenity(self, amenity_id: str, data) -> dict:
        """Update an amenity."""
        if not ObjectId.is_valid(amenity_id):
            raise NotFound("Amenity not found.")
        amenity = self.collection.find_one({"_id": ObjectId(amenity_id)})
        if not amenity:
            raise NotFound("Amenity not found.")

        updates = {}
        if data.get("name") is not None:
            updates["name"] = data["name"].strip()
        if data.get("description") is not None:
            updates["description"] = data["description"]
        if data.get("amount") is not None:
            if float(data["amount"]) <= 0:
                raise ValidationError("Amount must be a positive number.")
            updates["amount"] = float(data["amount"])

        updates["updated_at"] = datetime.utcnow()
        self.collection.update_one(
            {"_id": ObjectId(amenity_id)}, {"$set": updates}
        )
        return self._serialize(self.collection.find_one({"_id": ObjectId(amenity_id)}))

    def delete_amenity(self, amenity_id: str, user_id: str):
        """Soft delete an amenity."""
        if not ObjectId.is_valid(amenity_id):
            raise NotFound("Amenity not found.")
        amenity = self.collection.find_one({"_id": ObjectId(amenity_id)})
        if not amenity:
            raise NotFound("Amenity not found.")

        self.collection.update_one(
            {"_id": ObjectId(amenity_id)},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}},
        )
        log_activity(
            module="AMENITY",
            action="AMENITY_DELETED",
            performed_by=str(user_id),
            target_id=str(amenity_id),
            status="SUCCESS",
            description=f"Deleted amenity: {amenity.get('name')}.",
        )

    def _serialize(self, amenity: dict) -> dict:
        """Convert a raw MongoDB document into a serialized amenity dict."""
        if not amenity:
            return None
        return {
            "amenity_id": str(amenity.get("_id")),
            "name": amenity.get("name"),
            "description": amenity.get("description"),
            "amount": amenity.get("amount"),
            "is_active": amenity.get("is_active", True),
            "created_at": amenity.get("created_at"),
            "updated_at": amenity.get("updated_at"),
        }


class PaymentService:
    """Office payment business logic and orchestration."""

    GATEWAY = "RAZORPAY"

    def __init__(self):
        self.collection = get_collection(Collections.PAYMENTS)
        self.users_collection = get_collection(Collections.USERS)
        self._ensure_indexes()
        self.amenity_service = AmenityService()

    def _ensure_indexes(self):
        """Create required indexes if they do not exist."""
        existing = {index["name"] for index in self.collection.list_indexes()}
        if "employee_status_idx" not in existing:
            self.collection.create_index(
                [("employee_id", 1), ("status", 1)],
                name="employee_status_idx",
            )
        if "created_at_idx" not in existing:
            self.collection.create_index(
                [("created_at", -1)],
                name="created_at_idx",
            )
        if "amenity_idx" not in existing:
            self.collection.create_index(
                [("amenity_id", 1)],
                name="amenity_idx",
            )
        if "department_idx" not in existing:
            self.collection.create_index(
                [("department_id", 1)],
                name="department_idx",
            )
        if "gateway_order_id_unique" not in existing:
            self.collection.create_index(
                [("gateway_order_id", 1)],
                unique=True,
                sparse=True,
                name="gateway_order_id_unique",
            )
        if "gateway_payment_id_unique" not in existing:
            self.collection.create_index(
                [("gateway_payment_id", 1)],
                unique=True,
                sparse=True,
                name="gateway_payment_id_unique",
            )

    def create_payment(self, data) -> dict:
        """Create a new office payment and Razorpay order."""
        amenity_id = data.get("amenity_id")
        employee_id = data.get("employee_id")
        paid_by = data.get("paid_by")
        created_by = data.get("created_by")

        if not amenity_id or not str(amenity_id).strip():
            raise ValidationError("Amenity is required.")

        amenity = self.amenity_service.get_active_amenity(amenity_id)
        if not amenity:
            raise NotFound("Amenity not found or inactive.")

        employee = self.users_collection.find_one({"_id": ObjectId(employee_id)})
        if not employee:
            raise NotFound("Employee not found.")
        if not employee.get("is_active", True):
            raise PermissionDenied("Cannot create payment for an inactive employee.")

        amount = float(amenity.get("amount"))
        if amount <= 0:
            raise ValidationError("Invalid amenity amount.")

        customer_details = {
            "customer_id": employee_id,
            "customer_name": employee.get("full_name", ""),
            "customer_phone": employee.get("phone", ""),
        }
        if employee.get("email"):
            customer_details["customer_email"] = employee["email"]

        receipt = f"payment_{employee_id}_{int(time.time())}_{uuid.uuid4().hex[:8]}"

        backend_url = getattr(settings, "BACKEND_URL", "http://localhost:8000")
        return_url = f"{backend_url}/api/payment/callback/"
        notify_url = f"{backend_url}/api/payment/webhook/razorpay/"

        existing_pending = self._find_pending_payment(employee_id, amenity_id)
        if existing_pending:
            return {
                "payment_id": str(existing_pending.get("_id")),
                "order_id": existing_pending.get("gateway_order_id"),
                "amount": amount,
                "currency": "INR",
                "key_id": existing_pending.get("gateway_key_id"),
            }

        try:
            order = razorpay_gateway.create_order(
                amount=amount,
                currency="INR",
                receipt=receipt,
                customer_details=customer_details,
                return_url=return_url,
                notify_url=notify_url,
            )
        except Exception as e:
            raise ValidationError(f"Failed to create payment order: {str(e)}")

        order_data = order if isinstance(order, dict) else {}
        gateway_order_id = order_data.get("order_id")
        gateway_key_id = order_data.get("key_id")

        if not gateway_order_id:
            raise ValidationError("Razorpay did not return an order ID.")

        document = {
            "employee_id": employee_id,
            "paid_by": paid_by,
            "amenity_id": amenity_id,
            "amenity_name": amenity.get("name"),
            "amount": amount,
            "currency": "INR",
            "status": "PENDING",
            "gateway": self.GATEWAY,
            "gateway_order_id": gateway_order_id,
            "gateway_key_id": gateway_key_id,
            "gateway_payment_id": None,
            "payment_date": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "created_by": created_by,
        }
        payment_id = str(self.collection.insert_one(document).inserted_id)

        log_activity(
            module="PAYMENT",
            action="PAYMENT_CREATED",
            performed_by=str(created_by),
            target_id=payment_id,
            status="SUCCESS",
            description=f"Created payment: {amenity.get('name')} for employee {employee_id} (₹{amount}) via Razorpay.",
            metadata={
                "employee_id": employee_id,
                "amenity_id": amenity_id,
                "amount": amount,
                "paid_by": paid_by,
                "gateway": self.GATEWAY,
                "gateway_order_id": gateway_order_id,
            },
        )

        return {
            "payment_id": payment_id,
            "order_id": gateway_order_id,
            "amount": amount,
            "currency": "INR",
            "key_id": gateway_key_id,
        }

    def _find_pending_payment(self, employee_id, amenity_id) -> dict | None:
        """Find an existing pending payment for the same employee and amenity."""
        return self.collection.find_one({
            "employee_id": employee_id,
            "amenity_id": amenity_id,
            "status": "PENDING",
            "is_deleted": {"$ne": True},
        })

    def get_payment(self, payment_id: str) -> dict:
        """Get a payment by ID."""
        if not ObjectId.is_valid(payment_id):
            raise NotFound("Payment not found.")
        payment = self.collection.find_one({"_id": ObjectId(payment_id)})
        if not payment or payment.get("is_deleted"):
            raise NotFound("Payment not found.")
        return self._serialize(payment)

    def list_payments(
        self,
        employee_id=None,
        department_id=None,
        amenity_id=None,
        status=None,
        date=None,
        page=1,
        page_size=10,
    ):
        """List payments with optional filters."""
        query = {"is_deleted": {"$ne": True}}
        if employee_id:
            query["employee_id"] = employee_id
        if department_id:
            employee_ids = [
                str(e["_id"])
                for e in self.users_collection.find(
                    {"department_id": department_id, "is_deleted": {"$ne": True}},
                    {"_id": 1},
                )
            ]
            query["employee_id"] = {"$in": employee_ids}
        if amenity_id:
            query["amenity_id"] = amenity_id
        if status:
            query["status"] = status.upper()
        if date:
            try:
                filter_date = datetime.strptime(date, "%Y-%m-%d")
                next_date = filter_date + timedelta(days=1)
                query["created_at"] = {"$gte": filter_date, "$lt": next_date}
            except ValueError:
                pass

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
            "payments": [self._serialize(p) for p in records],
            "total_records": total_records,
            "total_pages": total_pages,
            "page": page,
            "page_size": page_size,
        }

    def verify_payment(self, payment_id, data, user_id) -> dict:
        """Verify a Razorpay payment using the Checkout signature.

        The frontend forwards the three values Razorpay returns after a
        successful Checkout: ``razorpay_order_id``, ``razorpay_payment_id`` and
        ``razorpay_signature``. The backend re-derives the signature with the
        key secret and only marks the payment as PAID on a match. We never
        trust the frontend status alone.
        """
        if not ObjectId.is_valid(payment_id):
            raise NotFound("Payment not found.")
        payment = self.collection.find_one({"_id": ObjectId(payment_id)})
        if not payment or payment.get("is_deleted"):
            raise NotFound("Payment not found.")
        if payment.get("status") == "PAID":
            raise ValidationError("Payment is already verified.")
        if payment.get("status") == "CANCELLED":
            raise ValidationError("Cannot verify a cancelled payment.")

        razorpay_order_id = (
            data.get("razorpay_order_id")
            or data.get("gateway_order_id")
            or payment.get("gateway_order_id")
        )
        razorpay_payment_id = (
            data.get("razorpay_payment_id") or data.get("gateway_payment_id")
        )
        razorpay_signature = data.get("razorpay_signature")

        if not (razorpay_order_id and razorpay_payment_id and razorpay_signature):
            raise ValidationError(
                "Missing Razorpay verification parameters (order_id, payment_id, signature)."
            )

        if str(razorpay_order_id) != str(payment.get("gateway_order_id")):
            raise ValidationError("Razorpay order id does not match the payment record.")

        if not razorpay_gateway.verify_payment_signature(
            str(razorpay_order_id), str(razorpay_payment_id), str(razorpay_signature)
        ):
            log_activity(
                module="PAYMENT",
                action="PAYMENT_FAILED",
                performed_by=str(user_id),
                target_id=str(payment_id),
                status="FAILED",
                description=f"Payment verification failed (bad signature) for payment {payment_id}.",
            )
            raise ValidationError("Payment verification failed. Invalid Razorpay signature.")

        updates = {
            "status": "PAID",
            "gateway_payment_id": str(razorpay_payment_id),
            "gateway_order_id": str(razorpay_order_id),
            "payment_date": datetime.utcnow(),
            "updated_by": user_id,
        }
        self.collection.update_one(
            {"_id": ObjectId(payment_id)}, {"$set": updates}
        )
        payment = self.collection.find_one({"_id": ObjectId(payment_id)})

        log_activity(
            module="PAYMENT",
            action="PAYMENT_VERIFIED",
            performed_by=str(user_id),
            target_id=str(payment_id),
            status="SUCCESS",
            description=f"Payment verified successfully: {payment.get('amenity_name')}.",
            metadata={
                "employee_id": payment.get("employee_id"),
                "amenity_id": payment.get("amenity_id"),
                "amount": payment.get("amount"),
                "gateway": self.GATEWAY,
                "gateway_order_id": str(razorpay_order_id),
                "gateway_payment_id": str(razorpay_payment_id),
            },
        )
        return self._serialize(payment)

    def cancel_payment(self, payment_id, user_id) -> dict:
        """Cancel a pending payment."""
        if not ObjectId.is_valid(payment_id):
            raise NotFound("Payment not found.")
        payment = self.collection.find_one({"_id": ObjectId(payment_id)})
        if not payment or payment.get("is_deleted"):
            raise NotFound("Payment not found.")
        if payment.get("status") == "PAID":
            raise ValidationError("Paid payment cannot be cancelled.")
        if payment.get("status") == "CANCELLED":
            raise ValidationError("Payment is already cancelled.")

        self.collection.update_one(
            {"_id": ObjectId(payment_id)},
            {"$set": {"status": "CANCELLED", "updated_by": user_id, "updated_at": datetime.utcnow()}},
        )
        payment = self.collection.find_one({"_id": ObjectId(payment_id)})

        log_activity(
            module="PAYMENT",
            action="PAYMENT_CANCELLED",
            performed_by=str(user_id),
            target_id=str(payment_id),
            status="SUCCESS",
            description=f"Payment cancelled: {payment.get('amenity_name')}.",
        )
        return self._serialize(payment)

    def _serialize(self, payment: dict) -> dict:
        """Convert a raw MongoDB document into a serialized payment dict."""
        if not payment:
            return None
        return {
            "payment_id": str(payment.get("_id")),
            "employee_id": payment.get("employee_id"),
            "paid_by": payment.get("paid_by"),
            "amenity_id": payment.get("amenity_id"),
            "amenity_name": payment.get("amenity_name"),
            "amount": payment.get("amount"),
            "currency": payment.get("currency", "INR"),
            "status": payment.get("status"),
            "gateway": payment.get("gateway", self.GATEWAY),
            "gateway_order_id": payment.get("gateway_order_id"),
            "gateway_payment_id": payment.get("gateway_payment_id"),
            "gateway_key_id": payment.get("gateway_key_id"),
            "payment_date": payment.get("payment_date"),
            "created_at": payment.get("created_at"),
            "updated_at": payment.get("updated_at"),
        }
