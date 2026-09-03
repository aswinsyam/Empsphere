from django.urls import path

from apps.reports.views import ReportView

urlpatterns = [
    path("employees/", ReportView.as_view(), name="report-employees"),
    path("attendance/", ReportView.as_view(), name="report-attendance"),
    path("leaves/", ReportView.as_view(), name="report-leaves"),
    path("departments/", ReportView.as_view(), name="report-departments"),
    path("designations/", ReportView.as_view(), name="report-designations"),
    path("activity/", ReportView.as_view(), name="report-activity"),
]
