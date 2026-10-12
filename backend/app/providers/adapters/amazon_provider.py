"""Amazon Provider Adapter for ShopQ.

NOTE: Amazon is strictly an OPTIONAL adapter, NEVER a hard system dependency.
If credentials, network scrapers, or anti-bot protections block live Amazon access,
the adapter gracefully defaults to PARTIAL or MOCK status without crashing or
halting system operations.
"""

import re
from typing import Optional, List
from urllib.parse import urlparse

from app.providers.base import BaseProvider
from app.providers.models import ProviderStatus, ProviderOffer
from app.providers.pipeline.pipeline import extraction_pipeline
from app.core.logging import logger


class AmazonProvider(BaseProvider):
    """
    Amazon India (amazon.in) product adapter.
    Optional adapter: failure never degrades the primary ShopQ workflow.
    """

    ALLOWED_DOMAINS = ["amazon.in", "amazon.com"]

    ASIN_PATTERN = re.compile(r'(?:/dp/|/gp/product/|/product/)([A-Z0-9]{10})', re.IGNORECASE)

    def __init__(self, scraper_client=None):
        super().__init__(
            retailer_id="amazon",
            display_name="Amazon India",
            allowed_domains=self.ALLOWED_DOMAINS,
            status=ProviderStatus.PARTIAL,
            is_optional=True,  # Crucial: Amazon is an optional adapter
        )
        self.scraper_client = scraper_client

    def check_health(self) -> ProviderStatus:
        """Health check returns status without throwing dependencies."""
        if self.scraper_client and getattr(self.scraper_client, "status", None) == ProviderStatus.LIVE:
            self.status = ProviderStatus.LIVE
        else:
            self.status = ProviderStatus.PARTIAL
        return self.status

    def extract_asin(self, url: str) -> Optional[str]:
        """Extracts 10-character Amazon Standard Identification Number (ASIN)."""
        if not url:
            return None
        match = self.ASIN_PATTERN.search(url)
        return match.group(1).upper() if match else None

    def fetch_and_extract(self, url: str) -> Optional[ProviderOffer]:
        """
        Attempts live fetch via ScraperAPI client if registered,
        then runs the deterministic extraction pipeline.
        Gracefully returns None if blocked or unavailable.
        """
        if not self.can_handle_url(url):
            return None

        if self.scraper_client:
            try:
                offer = self.scraper_client.fetch_and_extract(url)
                if offer:
                    offer.retailer = "amazon"
                    offer.retailer_name = "Amazon"
                    return offer
            except Exception as e:
                logger.warning(f"Optional Amazon adapter live fetch failed: {str(e)}")

        return None

    def search(self, query: str, limit: int = 5) -> List[ProviderOffer]:
        """Searches via scraper client if query is a URL."""
        if self.can_handle_url(query):
            single = self.fetch_and_extract(query)
            return [single] if single else []
        return []

    def get_by_id(self, product_id: str) -> Optional[ProviderOffer]:
        """Looks up by ASIN."""
        return None
