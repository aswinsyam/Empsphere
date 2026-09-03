"""
Seed default office amenities for TEST MODE.

IMPORTANT: These are temporary TEST MODE amounts for development/testing only.
For production, use real amounts via the admin panel or update this seed command.

Usage:
    python manage.py seed_amenities
"""
from datetime import datetime

from django.core.management.base import BaseCommand

from apps.common.constants import Collections
from apps.common.database import mongo


# TEST MODE AMOUNTS - Very small values for testing Razorpay Test Mode
# TODO: Replace with real amounts for production
DEFAULT_AMENITIES = [
    {
        "name": "Employee ID Card",
        "description": "Official company identification card for employee access and verification",
        "amount": 5.00,
    },
    {
        "name": "Company T-Shirt",
        "description": "Company branded employee T-shirt (premium cotton)",
        "amount": 10.00,
    },
    {
        "name": "Training Material",
        "description": "Professional training materials and course handbook",
        "amount": 20.00,
    },
    {
        "name": "Office Event",
        "description": "Registration fee for company events and team activities",
        "amount": 10.00,
    },
    {
        "name": "Employee Kit",
        "description": "Welcome kit including notebook, pen, and company merchandise",
        "amount": 20.00,
    },
    {
        "name": "Equipment Service",
        "description": "Maintenance and service charge for company-provided equipment",
        "amount": 5.00,
    },
]


class Command(BaseCommand):
    """Seed default office amenities for TEST MODE."""

    help = "Seed default office amenities for payment processing (TEST MODE amounts)."

    def handle(self, *args, **options):
        collection = mongo[Collections.AMENITIES]

        seeded_count = 0
        skipped_count = 0
        updated_count = 0

        for amenity in DEFAULT_AMENITIES:
            existing = collection.find_one({"name": amenity["name"]})
            if existing:
                # Update amount if it changed (for test mode updates)
                if existing.get("amount") != amenity["amount"]:
                    collection.update_one(
                        {"name": amenity["name"]},
                        {"$set": {"amount": amenity["amount"]}},
                    )
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS("Updated: %s (Rs.%.2f)" % (amenity["name"], amenity["amount"]))
                    )
                else:
                    skipped_count += 1
                    self.stdout.write(
                        self.style.WARNING("Skipped (exists): %s" % amenity["name"])
                    )
                continue

            collection.insert_one({
                "name": amenity["name"],
                "description": amenity["description"],
                "amount": amenity["amount"],
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            })
            seeded_count += 1
            self.stdout.write(
                self.style.SUCCESS("Created: %s (Rs.%.2f)" % (amenity["name"], amenity["amount"]))
            )

        self.stdout.write(
            self.style.SUCCESS(
                "\nAmenities seeding complete: %d created, %d updated, %d skipped." % (seeded_count, updated_count, skipped_count)
            )
        )
        self.stdout.write(
            self.style.WARNING("NOTE: These are TEST MODE amounts. Update for production use.")
        )
