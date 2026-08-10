"""
Email service.

Sends transactional emails using Django's SMTP backend.
"""

from __future__ import annotations

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import logging

from apps.common.config.settings import settings


logger = logging.getLogger(__name__)


class EmailService:
    """Sends HTML emails.

    In development it's common not to have an SMTP server configured. To
    avoid HTTP 500 errors when SMTP is unreachable, this method catches
    SMTP/connection errors, logs a warning, and continues. When email
    sending fails we still return normally so higher-level flows (OTP,
    registration) can proceed in development.
    """

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

        try:
            message.send(fail_silently=False)
        except Exception as exc:  # network/SMTP failures should not crash dev flows
            logger.warning(
                "Email send failed (subject=%s to=%s): %s",
                subject,
                to_emails,
                exc,
            )
