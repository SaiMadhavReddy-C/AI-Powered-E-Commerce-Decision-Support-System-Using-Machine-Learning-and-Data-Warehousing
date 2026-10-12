"""Demand-Driven Ingestion Trigger Handler for ShopQ.

Processes on-demand data acquisition triggers:
1. User Search Trigger (user query or direct URL search)
2. URL Check Trigger (user paste URL or product check)
3. Watchlist Update Trigger (scheduled or user-driven refresh for watched items)

Applies caching, SSRF allowlist protection, and seamless fallback to MockProvider.
"""

import time
import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse

from app.providers.models import ProviderOffer
from app.providers.registry import provider_registry
from app.core.config import settings
from app.core.logging import logger


class IngestionCacheEntry:
    """In-memory cache entry with expiration TTL."""

    def __init__(self, offer: ProviderOffer, ttl_seconds: float = 300.0):
        self.offer = offer
        self.expires_at = time.time() + ttl_seconds

    def is_expired(self) -> bool:
        return time.time() > self.expires_at


class DemandDrivenTriggerHandler:
    """
    Coordinates demand-driven data collection events initiated by user actions
    or system watchers. Prevents background crawling while guaranteeing fresh data.
    """

    def __init__(self, cache_ttl_seconds: float = 300.0):
        self._cache: Dict[str, IngestionCacheEntry] = {}
        self.cache_ttl_seconds = cache_ttl_seconds

    def handle_user_search_trigger(self, query: str, limit: int = 20) -> List[ProviderOffer]:
        """
        Trigger 1: User Search Trigger.
        Executes search via registered providers. If query is a URL, resolves directly.
        """
        if not query or not query.strip():
            return provider_registry.search("", limit=limit)

        clean_query = query.strip()

        # If query is a URL, invoke URL check trigger
        if (
            clean_query.startswith("http://")
            or clean_query.startswith("https://")
            or ".com" in clean_query
            or ".in" in clean_query
        ):
            single = self.handle_url_check_trigger(clean_query)
            return [single] if single else []

        # Standard keyword query
        return provider_registry.search(clean_query, limit=limit)

    def handle_url_check_trigger(self, url: str, force_refresh: bool = False) -> ProviderOffer:
        """
        Trigger 2: URL Check Trigger.
        Processes user-pasted product URLs.
        Checks observation cache before executing live fetch via ProviderRegistry.
        """
        clean_url = url.strip()

        # Check in-memory observation cache
        if not force_refresh and clean_url in self._cache:
            entry = self._cache[clean_url]
            if not entry.is_expired():
                logger.info(f"Serving cached observation for URL: {clean_url}")
                return entry.offer

        # Execute demand-driven fetch via ProviderRegistry
        offer = provider_registry.fetch_offer(clean_url)

        # Store in cache
        if offer:
            self._cache[clean_url] = IngestionCacheEntry(offer, ttl_seconds=self.cache_ttl_seconds)

        return offer

    def handle_watchlist_update_trigger(
        self,
        product_id_or_url: str,
        target_price: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Trigger 3: Watchlist Update Trigger.
        Runs a fresh observation check for a product on a user's watchlist.
        Evaluates whether the current price satisfies the target buy point.
        """
        # Determine whether input is URL or ID
        if product_id_or_url.startswith("http://") or product_id_or_url.startswith("https://"):
            offer = self.handle_url_check_trigger(product_id_or_url, force_refresh=True)
        else:
            # Check mock catalog by ID
            offer = provider_registry.get_by_id(product_id_or_url)
            if not offer:
                # Search by ID
                offers = provider_registry.search(product_id_or_url, limit=1)
                offer = offers[0] if offers else None

        if not offer:
            return {
                "success": False,
                "product_id": product_id_or_url,
                "error": "Unable to resolve product offer for watchlist update.",
            }

        price_dropped = False
        savings = 0.0

        if target_price is not None and target_price > 0:
            if offer.price <= target_price:
                price_dropped = True
                savings = max(0.0, target_price - offer.price)

        return {
            "success": True,
            "product_id": product_id_or_url,
            "retailer": offer.retailer_name,
            "product_title": offer.product_title,
            "current_price": offer.price,
            "target_price": target_price,
            "price_dropped": price_dropped,
            "savings": savings,
            "observed_at": offer.observed_at,
            "collected_at": offer.collected_at,
            "availability": offer.availability,
            "confidence_score": offer.confidence_score,
            "source_type": offer.source_type,
        }

    def clear_cache(self) -> None:
        """Clears in-memory ingestion cache."""
        self._cache.clear()


trigger_handler = DemandDrivenTriggerHandler()
