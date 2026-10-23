"""Application configuration and security settings for ShopQ."""

import os
from typing import List, Set


class SecuritySettings:
    """Security and environment configuration parameters."""

    def __init__(self) -> None:
        self.ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development").lower()
        self.IS_PRODUCTION: bool = self.ENVIRONMENT == "production"

        if self.IS_PRODUCTION:
            self.DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
        else:
            self.DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")

        self.PROJECT_NAME: str = os.getenv("PROJECT_NAME", "ShopQ Backend API")
        self.VERSION: str = os.getenv("VERSION", "1.0.0")
        self.API_PREFIX: str = os.getenv("API_PREFIX", "/api")
        self.SERVER_HOST: str = os.getenv("HOST", "0.0.0.0")
        self.SERVER_PORT: int = int(os.getenv("PORT", "8000"))
        self.MODEL_VERSION: str = os.getenv("MODEL_VERSION", "shopq-decision-v2.1")
        self.DECISION_RULES_VERSION: str = os.getenv("DECISION_RULES_VERSION", "rules-2026.10")
        self.MATCHING_MODEL_VERSION: str = os.getenv("MATCHING_MODEL_VERSION", "match-v1")

        # Supported retailer domains
        self.ALLOWED_RETAILER_DOMAINS: Set[str] = {
            "amazon.in",
            "flipkart.com",
            "croma.com",
            "reliancedigital.in",
            "tatacliq.com",
            "myntra.com",
            "ajio.com",
            "meesho.com",
            "jiomart.com",
            "nykaa.com",
        }

        # CORS settings (strip whitespace and trailing slashes for clean origin matching)
        allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
        if allowed_origins_env.strip():
            self.ALLOWED_ORIGINS: List[str] = [
                origin.strip().rstrip("/")
                for origin in allowed_origins_env.split(",")
                if origin.strip()
            ]
        else:
            # Development defaults + Vercel wildcard preview domains
            self.ALLOWED_ORIGINS: List[str] = [
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "http://localhost:3000",
                "http://localhost:4173",
                # Vercel production & preview deployments
                "https://shopq.vercel.app",
                "https://ai-powered-e-commerce-decision-support-system-using-machine-learning-and-data-warehousing.vercel.app",
            ]
        self.CORS_ORIGINS: List[str] = self.ALLOWED_ORIGINS

        # Rate limiting settings for /api/analyze
        self.RATE_LIMIT_ANALYZE_RPM: int = int(os.getenv("RATE_LIMIT_ANALYZE_RPM", "10"))
        self.RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))

        # SSRF validation network timeout
        self.SSRF_TIMEOUT_SECONDS: float = float(os.getenv("SSRF_TIMEOUT_SECONDS", "5.0"))

        # Third-party data provider keys
        self.SCRAPERAPI_KEY: str = os.getenv("SCRAPERAPI_KEY", "")

        # API keys and secrets
        self.GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
        self.SECRET_KEY: str = os.getenv(
            "SECRET_KEY", "shopq-dev-secret-key-change-in-production"
        )
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()


settings = SecuritySettings()

