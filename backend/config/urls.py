"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.authentication.urls')),
    path('api/organization/', include('apps.organization.urls')),
    path('api/employees/', include('apps.employee.urls')),
    path('api/attendance/', include('apps.attendance.urls')),
    path('api/leaves/', include('apps.leave.urls')),
    path('api/activity-logs/', include('apps.activity_logs.urls')),
    path('api/statistics/', include('apps.statistics.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/payment/', include('apps.payment.urls')),
]