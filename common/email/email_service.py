"""
Common Email Service.
Handles email sending across the application.
"""
from __future__ import annotations

import smtplib
from email.message import EmailMessage


class EmailService:
    """Email sending logic."""

    def send(self, dto):
        """Send email."""
        email = dto.get("email")
        subject = dto.get("subject")
        body = dto.get("body")
        # In real implementation, would use SMTP
        return {
            "message": f"Email sent to {email}",
            "subject": subject,
        }