"""Groundmail transactional email integration."""

import json
import urllib.error
import urllib.request
from typing import Optional

from app.core.config import settings
from app.core.logging import logger


class EmailService:
    API_URL = "https://api.groundmail.dev/emails"

    def send(self, recipient: str, subject: str, html: str, text: Optional[str] = None) -> dict:
        if not settings.GROUNDMAIL_API_KEY or not settings.GROUNDMAIL_FROM_EMAIL:
            raise RuntimeError("Groundmail is not configured")
        body = {
            "from": settings.GROUNDMAIL_FROM_EMAIL,
            "to": recipient,
            "subject": subject,
            "html": html,
            "text": text or "ShopQ notification",
            "category": "transactional",
        }
        request = urllib.request.Request(
            self.API_URL,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {settings.GROUNDMAIL_API_KEY}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError) as error:
            logger.warning(f"Groundmail send failed: {error}")
            raise RuntimeError("Email delivery failed") from error


email_service = EmailService()
