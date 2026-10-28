"""Firecrawl-backed, demand-driven product extraction."""

import datetime
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional

from app.core.config import settings
from app.core.logging import logger
from app.providers.base import BaseProvider
from app.providers.models import ProviderOffer, ProviderStatus


class FirecrawlProvider(BaseProvider):
    """Extracts a verified offer from one explicitly supplied retailer URL."""

    ALLOWED_RETAILER_DOMAINS = [
        "amazon.in", "amzn.in", "flipkart.com", "croma.com", "reliancedigital.in",
        "tatacliq.com", "myntra.com", "ajio.com", "meesho.com", "jiomart.com", "nykaa.com",
    ]
    API_URL = "https://api.firecrawl.dev/v2/scrape"
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = (api_key or settings.FIRECRAWL_API_KEY).strip()
        super().__init__(
            retailer_id="firecrawl",
            display_name="Firecrawl Product Extractor",
            allowed_domains=self.ALLOWED_RETAILER_DOMAINS,
            status=ProviderStatus.LIVE if self.api_key else ProviderStatus.UNAVAILABLE,
            is_optional=False,
        )
        self.timeout_seconds = settings.FIRECRAWL_TIMEOUT_SECONDS

    def can_handle_url(self, url: str) -> bool:
        try:
            parsed = urllib.parse.urlparse(url)
            host = (parsed.hostname or "").lower()
            return parsed.scheme in ("http", "https") and any(
                host == domain or host.endswith(f".{domain}")
                for domain in self.ALLOWED_RETAILER_DOMAINS
            )
        except ValueError:
            return False

    def check_health(self) -> ProviderStatus:
        self.status = ProviderStatus.LIVE if self.api_key else ProviderStatus.UNAVAILABLE
        return self.status

    @staticmethod
    def _price(value: Any) -> Optional[float]:
        if isinstance(value, (int, float)):
            return float(value) if value > 0 else None
        if isinstance(value, str):
            number = re.sub(r"[^0-9.]", "", value)
            try:
                parsed = float(number)
                return parsed if parsed > 0 else None
            except ValueError:
                return None
        return None

    @staticmethod
    def _retailer(url: str) -> tuple[str, str]:
        host = urllib.parse.urlparse(url).hostname or "retailer"
        retailer = host.lower().removeprefix("www.").split(".")[0]
        return retailer, retailer.replace("-", " ").title()

    @staticmethod
    def _is_product_page(title: str) -> bool:
        """Reject search/category titles that can contain an unrelated price."""
        lowered = title.lower()
        return not any(marker in lowered for marker in (
            "search results", "results for", "deals under", "under ₹", "under rs", "shop by category",
        ))

    def fetch_and_extract(self, url: str) -> Optional[ProviderOffer]:
        if not self.api_key or not self.can_handle_url(url):
            return None

        schema: Dict[str, Any] = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "price": {"type": ["number", "string"]},
                "currency": {"type": "string"},
                "availability": {"type": "string"},
                "seller": {"type": "string"},
                "image_url": {"type": "string"},
                "rating": {"type": ["number", "string"]},
                "review_count": {"type": ["number", "string"]},
            },
            "required": ["title", "price"],
        }
        payload = {
            "url": url,
            "formats": [{
                "type": "json",
                "schema": schema,
                "prompt": "Extract only the current product listing values. Do not estimate missing fields.",
            }],
            "location": {"country": "IN"},
        }
        request = urllib.request.Request(
            self.API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError) as error:
            logger.warning(f"Firecrawl extraction failed for {url}: {error}")
            return None

        data = body.get("data", {}) if isinstance(body, dict) else {}
        extracted = data.get("json", data.get("product", {})) if isinstance(data, dict) else {}
        if isinstance(extracted, str):
            try:
                extracted = json.loads(extracted)
            except ValueError:
                return None
        if not isinstance(extracted, dict):
            return None

        price = self._price(extracted.get("price"))
        title = str(extracted.get("title") or "").strip()
        if not title or price is None or not self._is_product_page(title):
            logger.info(f"Firecrawl returned a non-product page for {url}; rejecting offer")
            return None

        retailer, retailer_name = self._retailer(url)
        seller_name = str(extracted.get("seller") or retailer_name)
        availability = str(extracted.get("availability") or "UNKNOWN").upper().replace(" ", "_")
        if availability not in {"IN_STOCK", "OUT_OF_STOCK", "LIMITED_STOCK"}:
            availability = "UNKNOWN"
        rating = self._price(extracted.get("rating")) or 0.0
        reviews = int(self._price(extracted.get("review_count")) or 0)
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()

        return ProviderOffer(
            retailer=retailer,
            retailer_name=retailer_name,
            product_title=title,
            brand=title.split()[0] if title else None,
            price=price,
            currency=str(extracted.get("currency") or "INR").upper(),
            seller={
                "name": seller_name,
                "rating": rating,
                "reviews": reviews,
                "reviewCount": reviews,
                "reliability": "UNKNOWN",
                "returnPolicy": "Not verified",
                "warranty": "Not verified",
            },
            seller_name=seller_name,
            rating=rating,
            review_count=reviews,
            availability=availability,
            image_url=extracted.get("image_url"),
            product_url=url,
            observed_at=now,
            collected_at=now,
            source_type="FIRECRAWL",
            source_status="LIVE",
            confidence_score=0.85 if seller_name != retailer_name else 0.75,
            uncertain_fields=["seller"] if seller_name == retailer_name else [],
            extraction_stage="FIRECRAWL_JSON",
        )

    def search(self, query: str, limit: int = 5):
        """Find retailer pages, then verify each result through product extraction."""
        if not self.api_key or not query.strip():
            return []

        offers = []
        query_tokens = [token for token in re.split(r"[^a-z0-9]+", query.lower()) if len(token) >= 3]
        seen_urls = set()
        for domain in ("amazon.in", "flipkart.com", "croma.com"):
            payload = {
                "query": f"{query} site:{domain}",
                "limit": min(max(limit, 1), 3),
                "sources": [{"type": "web"}],
            }
            request = urllib.request.Request(
                "https://api.firecrawl.dev/v2/search",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            try:
                with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                    body = json.loads(response.read().decode("utf-8"))
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError) as error:
                logger.warning(f"Firecrawl search failed for {domain}: {error}")
                continue

            data = body.get("data", []) if isinstance(body, dict) else []
            if isinstance(data, dict):
                data = data.get("web", data.get("results", []))
            for result in data:
                url = result.get("url", "") if isinstance(result, dict) else ""
                if url in seen_urls or not self.can_handle_url(url):
                    continue
                seen_urls.add(url)
                offer = self.fetch_and_extract(url)
                title = (offer.product_title.lower() if offer else "")
                if offer and (not query_tokens or any(token in title for token in query_tokens)):
                    offers.append(offer)
                if len(offers) >= limit:
                    return offers
        return offers

    def get_by_id(self, product_id: str) -> Optional[ProviderOffer]:
        return None
