"""Django app configuration for the authentication app."""
from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """Configuration for the authentication app handling auth flows."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.authentication'
