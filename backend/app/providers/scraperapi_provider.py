"""ScraperAPI Provider for live web-data acquisition across Indian e-commerce platforms.

Features:
1. Uses SCRAPERAPI_KEY from backend environment variables (backend-only secret).
2. Accept ONLY explicitly requested product URLs (demand-driven, zero crawling).
3. Geotargeting (country_code=in for amazon.in, flipkart.com, croma.com, reliancedigital.in, myntra.com).
4. Normal requests first (render=false) with render=true fallback for dynamic JS hydration.
5. Respects credit limits & handles 429/quota errors gracefully by falling back to cache/mock.
6. 15s request timeout enforcement.
7. Returns normalized ProviderOffer with strict type safety.
"""

import os
import re
import urllib.parse
from typing import Optional, List, Dict, Any
import urllib.request
import urllib.error

from app.providers.base import BaseProvider
from app.providers.models import ProviderStatus, ProviderOffer
from app.providers.pipeline.pipeline import extraction_pipeline
from app.core.config import settings
from app.core.logging import logger


class ScraperAPIProvider(BaseProvider):
    """
    Live web extraction adapter powered by ScraperAPI proxy service.
    Designed exclusively for demand-driven product URL inspections.
    """

    ALLOWED_RETAILER_DOMAINS = [
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
    ]

    BASE_SCRAPERAPI_URL = "http://api.scraperapi.com"

    def __init__(self, api_key: Optional[str] = None):
        key = api_key or getattr(settings, "SCRAPERAPI_KEY", "") or os.getenv("SCRAPERAPI_KEY", "")
        self.api_key = key.strip() if key else ""

        # Determine initial operational status
        initial_status = ProviderStatus.LIVE if self.api_key else ProviderStatus.UNAVAILABLE

        super().__init__(
            retailer_id="scraperapi",
            display_name="ScraperAPI Live Gateway",
            allowed_domains=self.ALLOWED_RETAILER_DOMAINS,
            status=initial_status,
            is_optional=False,
        )

        self.timeout_seconds = 15.0
        self.consecutive_quota_errors = 0

    def check_health(self) -> ProviderStatus:
        """Evaluates API key readiness and rate limit status."""
        if not self.api_key:
            self.status = ProviderStatus.UNAVAILABLE
            return ProviderStatus.UNAVAILABLE

        if self.consecutive_quota_errors > 3:
            self.status = ProviderStatus.PARTIAL
            return ProviderStatus.PARTIAL

        self.status = ProviderStatus.LIVE
        return ProviderStatus.LIVE

    def can_handle_url(self, url: str) -> bool:
        """
        Validates that URL is an explicitly supported retailer domain.
        Rejects arbitrary external URLs, SSRF attempts, and IP addresses.
        """
        if not url:
            return False

        try:
            parsed = urllib.parse.urlparse(url)
            if parsed.scheme not in ("http", "https"):
                return False

            hostname = (parsed.hostname or "").lower()
            if not hostname:
                return False

            # SSRF Protection: Deny local and private addresses
            if hostname in ("localhost", "127.0.0.1", "0.0.0.0", "169.254.169.254"):
                return False
            if hostname.startswith("10.") or hostname.startswith("192.168."):
                return False

            return any(hostname == d or hostname.endswith(f".{d}") for d in self.ALLOWED_RETAILER_DOMAINS)
        except Exception:
            return False

    def fetch_page_content(self, target_url: str, render: bool = False) -> Optional[str]:
        """
        Executes HTTP GET via ScraperAPI with geotargeting (country_code=in).
        Applies a strict 15s timeout and gracefully catches 429/403 errors.
        """
        if not self.api_key:
            logger.info("ScraperAPI key missing; cannot perform live HTTP request.")
            return None

        if not self.can_handle_url(target_url):
            logger.warning(f"URL rejected by ScraperAPI allowlist/SSRF guard: {target_url}")
            return None

        # Build ScraperAPI parameters
        params = {
            "api_key": self.api_key,
            "url": target_url,
            "country_code": "in",  # Geotarget Indian e-commerce sites
            "render": "true" if render else "false",
        }
        query_string = urllib.parse.urlencode(params)
        request_url = f"{self.BASE_SCRAPERAPI_URL}?{query_string}"

        req = urllib.request.Request(
            request_url,
            headers={
                "User-Agent": "ShopQ-DataCollector/1.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
                if response.status == 200:
                    self.consecutive_quota_errors = 0
                    html = response.read().decode("utf-8", errors="replace")
                    return html
                else:
                    logger.warning(f"ScraperAPI non-200 response: {response.status}")
                    return None
        except urllib.error.HTTPError as e:
            if e.code in (429, 403):
                # Quota exceeded or rate limited
                self.consecutive_quota_errors += 1
                self.status = ProviderStatus.PARTIAL
                logger.warning(f"ScraperAPI quota/credit limit encountered (HTTP {e.code}): {e.reason}")
            else:
                logger.warning(f"ScraperAPI HTTP error {e.code} for URL {target_url}: {e.reason}")
            return None
        except urllib.error.URLError as e:
            logger.warning(f"ScraperAPI connection/timeout error for {target_url}: {str(e.reason)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected ScraperAPI exception: {str(e)}")
            return None

    def fetch_and_extract(self, url: str) -> Optional[ProviderOffer]:
        """
        Demand-driven ingestion pipeline:
        1. Validates requested URL against domain allowlist.
        2. Tries standard HTTP request first (render=false) to save credits.
        3. Falls back to render=true if initial HTML lacks product data.
        4. Runs deterministic extraction pipeline.
        """
        if not self.can_handle_url(url):
            return None

        # Pass 1: Standard request (render=false)
        html = self.fetch_page_content(url, render=False)

        offer: Optional[ProviderOffer] = None
        if html and len(html) > 500:
            offer = extraction_pipeline.run(html, url)

        # Pass 2: If standard request failed or produced no price, retry with rendering (render=true)
        if not offer and self.api_key and self.consecutive_quota_errors == 0:
            logger.info(f"Standard fetch incomplete for {url}. Retrying with JS rendering (render=true)...")
            rendered_html = self.fetch_page_content(url, render=True)
            if rendered_html and len(rendered_html) > 500:
                offer = extraction_pipeline.run(rendered_html, url)

        if offer:
            offer.source_type = "SCRAPERAPI"
            offer.source_status = self.status.value
            return offer

        return None

    def search(self, query: str, limit: int = 5) -> List[ProviderOffer]:
        """
        If search query is a URL, fetches it directly.
        ScraperAPI is strictly demand-driven and does not spider search indices directly.
        """
        if self.can_handle_url(query):
            single = self.fetch_and_extract(query)
            return [single] if single else []
        return []

    def get_by_id(self, product_id: str) -> Optional[ProviderOffer]:
        """ScraperAPI resolves via URL rather than internal ID."""
        return None
