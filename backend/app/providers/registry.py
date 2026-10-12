"""Provider Registry for ShopQ.

Central management registry for all retailer adapters and data acquisition providers:
- Amazon (AmazonProvider) [OPTIONAL ADAPTER]
- Flipkart (FlipkartProvider)
- Croma (CromaProvider)
- Reliance Digital (RelianceDigitalProvider)
- Myntra (MyntraProvider)
- ScraperAPI (ScraperAPIProvider) [PRIMARY LIVE GATEWAY]
- MockProvider (MockProvider) [100% RELIABLE ZERO-DOWNTIME FALLBACK]

Statuses: LIVE, PARTIAL, MOCK, UNAVAILABLE.
"""

from typing import Dict, Optional, List, Any
from urllib.parse import urlparse

from app.providers.base import BaseProvider
from app.providers.models import ProviderStatus, ProviderOffer
from app.providers.scraperapi_provider import ScraperAPIProvider
from app.providers.adapters.mock_provider import MockProvider
from app.providers.adapters.amazon_provider import AmazonProvider
from app.providers.adapters.flipkart_provider import FlipkartProvider
from app.providers.adapters.croma_provider import CromaProvider
from app.providers.adapters.reliance_provider import RelianceDigitalProvider
from app.providers.adapters.myntra_provider import MyntraProvider
from app.core.config import settings
from app.core.logging import logger


class ProviderRegistry:
    """
    Registry managing lifecycle, dispatching, and fallback hierarchies
    for all data providers.
    """

    def __init__(self):
        self._providers: Dict[str, BaseProvider] = {}
        self._domain_to_retailer: Dict[str, str] = {}

        # 1. Initialize MockProvider (Guaranteed baseline)
        self.mock_provider = MockProvider()
        self.register(self.mock_provider)

        # 2. Initialize ScraperAPI Provider (Live gateway)
        self.scraperapi_provider = ScraperAPIProvider()
        self.register(self.scraperapi_provider)

        # 3. Initialize specific retailer adapters
        self.amazon_provider = AmazonProvider(scraper_client=self.scraperapi_provider)
        self.flipkart_provider = FlipkartProvider(scraper_client=self.scraperapi_provider)
        self.croma_provider = CromaProvider(scraper_client=self.scraperapi_provider)
        self.reliance_provider = RelianceDigitalProvider(scraper_client=self.scraperapi_provider)
        self.myntra_provider = MyntraProvider(scraper_client=self.scraperapi_provider)

        self.register(self.amazon_provider)
        self.register(self.flipkart_provider)
        self.register(self.croma_provider)
        self.register(self.reliance_provider)
        self.register(self.myntra_provider)

        logger.info(
            f"ProviderRegistry initialized with {len(self._providers)} providers. "
            f"ScraperAPI status: {self.scraperapi_provider.status.value}"
        )

    def register(self, provider: BaseProvider) -> None:
        """Registers an adapter and maps its allowed domains."""
        self._providers[provider.retailer_id.lower()] = provider
        for domain in provider.allowed_domains:
            self._domain_to_retailer[domain.lower()] = provider.retailer_id.lower()

    def get_provider(self, retailer_id: str) -> Optional[BaseProvider]:
        """Looks up registered provider by retailer ID."""
        return self._providers.get(retailer_id.lower())

    def get_provider_for_url(self, url: str) -> BaseProvider:
        """
        Determines the most appropriate provider for a given URL.
        Defaults to ScraperAPIProvider if key is present, otherwise retailer adapter or MockProvider.
        """
        if not url:
            return self.mock_provider

        try:
            parsed = urlparse(url)
            hostname = (parsed.hostname or "").lower()

            for domain, retailer_id in self._domain_to_retailer.items():
                if hostname == domain or hostname.endswith(f".{domain}"):
                    # If ScraperAPI is active and live, use it
                    if self.scraperapi_provider.status == ProviderStatus.LIVE:
                        return self.scraperapi_provider
                    # Otherwise return the specific retailer provider
                    prov = self._providers.get(retailer_id)
                    if prov:
                        return prov
        except Exception:
            pass

        return self.mock_provider

    def fetch_offer(self, url: str, force_mock: bool = False) -> ProviderOffer:
        """
        Main demand-driven fetch execution:
        1. If force_mock is True, immediately returns MockProvider offer.
        2. If SCRAPERAPI_KEY is present and ScraperAPI is LIVE, attempts live extraction.
        3. If live extraction encounters an error, 429 quota limit, or blocks,
           gracefully falls back to MockProvider with adjusted confidence score.
        4. Amazon failure never halts the process (optional adapter).
        """
        if force_mock:
            return self._fetch_from_mock(url, reason="FORCE_MOCK")

        # Check if live extraction is feasible
        if self.scraperapi_provider.status == ProviderStatus.LIVE:
            try:
                live_offer = self.scraperapi_provider.fetch_and_extract(url)
                if live_offer:
                    return live_offer
                logger.info(f"Live fetch returned empty/invalid data for {url}; cascading to MockProvider fallback.")
            except Exception as e:
                logger.warning(f"Live provider exception on {url}: {str(e)}; cascading to MockProvider.")

        # Fallback to MockProvider
        return self._fetch_from_mock(url, reason="LIVE_UNAVAILABLE_OR_FALLBACK")

    def _fetch_from_mock(self, url: str, reason: str = "FALLBACK") -> ProviderOffer:
        """Resolves offer from MockProvider with fallback telemetry."""
        offer = self.mock_provider.fetch_and_extract(url)
        if not offer:
            # Generate synthetic mock offer
            offer = self.mock_provider._generate_synthetic_offer(url)

        # Annotate offer metadata
        offer.source_type = "MOCK"
        offer.source_status = "MOCK"
        if reason != "FORCE_MOCK":
            offer.raw_metadata["fallback_reason"] = reason
            offer.confidence_score = min(offer.confidence_score, 0.85)

        return offer

    def search(self, query: str, limit: int = 5) -> List[ProviderOffer]:
        """
        Executes demand-driven search across registered providers.
        If live providers are unavailable, falls back to MockProvider.
        """
        if not query:
            return self.mock_provider.search("", limit=limit)

        # If query is a URL, fetch offer directly
        if query.startswith("http://") or query.startswith("https://") or ".com" in query or ".in" in query:
            offer = self.fetch_offer(query)
            return [offer] if offer else []

        # Return mock catalog search results
        return self.mock_provider.search(query, limit=limit)

    def get_by_id(self, product_id: str) -> Optional[ProviderOffer]:
        """Retrieves offer by product ID or scenario slug."""
        return self.mock_provider.get_by_id(product_id)

    def get_status_summary(self) -> Dict[str, str]:
        """Returns the health status of all registered adapters."""
        summary: Dict[str, str] = {}
        for rid, provider in self._providers.items():
            summary[rid] = provider.status.value
        return summary

    def get_status(self, retailer_id: str) -> ProviderStatus:
        """Returns status for a specific provider."""
        provider = self.get_provider(retailer_id)
        return provider.status if provider else ProviderStatus.UNAVAILABLE


provider_registry = ProviderRegistry()
