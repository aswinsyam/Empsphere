from apps.common.database import get_collection
from apps.common.constants import Collections


class StatisticsService:
    """Aggregates dashboard statistics from MongoDB."""

    @staticmethod
    def get_dashboard_stats():
        """Return summary counts for the dashboard."""
        users_collection = get_collection(Collections.USERS)
        departments_collection = get_collection(Collections.DEPARTMENTS)
        attendance_collection = get_collection(Collections.ATTENDANCE)
        leaves_collection = get_collection(Collections.LEAVES)

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
