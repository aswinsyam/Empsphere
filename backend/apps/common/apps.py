"""Django app configuration for the common app."""
from django.apps import AppConfig


class CommonConfig(AppConfig):
    """Configuration for the common app which houses shared utilities."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.common'
