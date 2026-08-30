"""
Statistics Service.
Aggregates counts from multiple collections.
"""

from apps.common.database.mongo import mongo
from apps.common.core.collections import Collections


class StatisticsService:
    """Aggregates dashboard statistics from MongoDB."""

    @staticmethod
    def get_dashboard_stats():
        """Return summary counts for the dashboard."""
        users_collection = mongo.get_collection(Collections.USERS)
        departments_collection = mongo.get_collection(Collections.DEPARTMENTS)
        attendance_collection = mongo.get_collection(Collections.ATTENDANCE)
        leaves_collection = mongo.get_collection(Collections.LEAVES)

        total_employees = users_collection.count_documents({})
        total_departments = departments_collection.count_documents({})
        total_attendance = attendance_collection.count_documents({})
        pending_leaves = leaves_collection.count_documents({"status": "PENDING"})

        return {
            "total_employees": total_employees,
            "total_departments": total_departments,
            "total_attendance": total_attendance,
            "pending_leaves": pending_leaves,
        }
