"""
Statistics Controller.
Exposes dashboard statistics via REST API.
"""

from rest_framework.views import APIView

from apps.common.base.base_controller import BaseController
from apps.common.decorators.permission import require_role
from apps.common.core.roles import Role
from apps.statistics.services.statistics_service import StatisticsService


class StatisticsController(BaseController, APIView):
    """Returns dashboard statistics."""

    @require_role(
        Role.SUPER_ADMIN,
        Role.ADMIN,
        Role.HR_MANAGER,
        Role.EMPLOYEE,
    )
    def get(self, request):
        """Return summary stats."""
        stats = StatisticsService.get_dashboard_stats()
        return self.success(
            message="Dashboard statistics fetched successfully.",
            data=stats,
            meta=None,
        )
