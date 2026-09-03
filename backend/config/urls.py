"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.urls import include, path

urlpatterns = [
    path('api/auth/', include('apps.authentication.urls')),
    path('api/departments/', include('apps.departments.urls')),
    path('api/designations/', include('apps.designations.urls')),
    path('api/employees/', include('apps.employees.urls')),
    path('api/attendance/', include('apps.attendance.urls')),
    path('api/leaves/', include('apps.leaves.urls')),
    path('api/activity-logs/', include('apps.activity_logs.urls')),
    path('api/statistics/', include('apps.statistics.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/payments/', include('apps.payments.urls')),
]
