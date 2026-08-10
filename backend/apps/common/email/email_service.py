"""
Email service.

Sends transactional emails using Django's SMTP backend.
"""

from __future__ import annotations

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from apps.common.config.settings import settings


class EmailService:
    """Sends HTML emails."""

    @staticmethod
    def send(
        subject: str,
        to_emails: list[str],
        template_name: str,
        context: dict | None = None,
    ):
        """Render a template and send an email to the given addresses."""
        context = context or {}

        html_body = render_to_string(template_name, context)

        message = EmailMultiAlternatives(
            subject=subject,
            body=html_body,
            from_email=settings.EMAIL_HOST_USER or None,
            to=to_emails,
        )
        message.attach_alternative(html_body, "text/html")
        message.send(fail_silently=False)
