"""
Reports API URL routes.
"""

from django.urls import path

from apps.reports.controllers.report_controller import ReportController

urlpatterns = [
    path("employees/", ReportController.as_view(), name="report-employees"),
    path("attendance/", ReportController.as_view(), name="report-attendance"),
    path("leaves/", ReportController.as_view(), name="report-leaves"),
    path("departments/", ReportController.as_view(), name="report-departments"),
    path("designations/", ReportController.as_view(), name="report-designations"),
    path("activity/", ReportController.as_view(), name="report-activity"),
]
