import hashlib
import secrets
import threading
import time
from typing import Dict, Optional

from app.services.email_service import email_service


class AuthService:
    OTP_TTL_SECONDS = 600
    RESEND_COOLDOWN_SECONDS = 30

    def __init__(self):
        self._lock = threading.Lock()
        self._otps: Dict[str, dict] = {}
        self._sessions: Dict[str, str] = {}

    def request_otp(self, email: str) -> dict:
        normalized = email.strip().lower()
        now = time.time()
        with self._lock:
            previous = self._otps.get(normalized)
            if previous and now - previous["sent_at"] < self.RESEND_COOLDOWN_SECONDS:
                return {"expiresIn": max(0, int(previous["expires_at"] - now)), "resendIn": self.RESEND_COOLDOWN_SECONDS - int(now - previous["sent_at"])}
            code = f"{secrets.randbelow(1_000_000):06d}"
            self._otps[normalized] = {"hash": hashlib.sha256(code.encode()).hexdigest(), "sent_at": now, "expires_at": now + self.OTP_TTL_SECONDS}
        email_service.send(normalized, "Your ShopQ login code", f"<p>Your ShopQ login code is <strong>{code}</strong>.</p><p>This code expires in 10 minutes.</p>", f"Your ShopQ login code is {code}. It expires in 10 minutes.")
        return {"expiresIn": self.OTP_TTL_SECONDS, "resendIn": self.RESEND_COOLDOWN_SECONDS}

    def verify_otp(self, email: str, code: str) -> Optional[str]:
        normalized = email.strip().lower()
        with self._lock:
            record = self._otps.get(normalized)
            if not record or time.time() > record["expires_at"] or hashlib.sha256(code.strip().encode()).hexdigest() != record["hash"]:
                return None
            del self._otps[normalized]
            token = secrets.token_urlsafe(32)
            self._sessions[token] = normalized
            return token


auth_service = AuthService()
