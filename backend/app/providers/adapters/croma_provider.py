"""Croma Provider Adapter for ShopQ."""

from typing import Optional, List

from app.providers.base import BaseProvider
from app.providers.models import ProviderStatus, ProviderOffer
from app.core.logging import logger


class CromaProvider(BaseProvider):
    """Croma Electronics adapter (croma.com)."""

    ALLOWED_DOMAINS = ["croma.com"]

    def __init__(self, scraper_client=None):
        super().__init__(
            retailer_id="croma",
            display_name="Croma",
            allowed_domains=self.ALLOWED_DOMAINS,
            status=ProviderStatus.PARTIAL,
            is_optional=False,
        )
        self.scraper_client = scraper_client

    def check_health(self) -> ProviderStatus:
        if self.scraper_client and getattr(self.scraper_client, "status", None) == ProviderStatus.LIVE:
            self.status = ProviderStatus.LIVE
        else:
            self.status = ProviderStatus.PARTIAL
        return self.status

    def fetch_and_extract(self, url: str) -> Optional[ProviderOffer]:
        if not self.can_handle_url(url):
            return None

        if self.scraper_client:
            try:
                offer = self.scraper_client.fetch_and_extract(url)
                if offer:
                    offer.retailer = "croma"
                    offer.retailer_name = "Croma"
                    return offer
            except Exception as e:
                logger.warning(f"Croma adapter fetch failed: {str(e)}")

        return None

    def search(self, query: str, limit: int = 5) -> List[ProviderOffer]:
        if self.can_handle_url(query):
            single = self.fetch_and_extract(query)
            return [single] if single else []
        return []

    def get_by_id(self, product_id: str) -> Optional[ProviderOffer]:
        return None
