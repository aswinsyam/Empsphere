from rest_framework.views import APIView

from apps.common.permissions import require_role
from apps.common.responses import success
from apps.statistics.services import StatisticsService


class StatisticsView(APIView):
    """Returns dashboard statistics."""

    @require_role(
        "SUPER_ADMIN",
        "ADMIN",
        "HR_MANAGER",
        "EMPLOYEE",
    )
    def get(self, request):
        """Return summary stats."""
        stats = StatisticsService.get_dashboard_stats()
        return success("Dashboard statistics retrieved.", stats)
