"""
Statistics app URL routes.
"""

from django.urls import path

from apps.statistics.controllers.statistics_controller import (
    StatisticsController,
)

urlpatterns = [
    path(
        "",
        StatisticsController.as_view(),
        name="dashboard-statistics",
    ),
]
