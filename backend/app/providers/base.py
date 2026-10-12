"""Base Provider Interface and Abstract Class for ShopQ Retailer Adapters."""

from abc import ABC, abstractmethod
from typing import Optional, List
from urllib.parse import urlparse

from app.providers.models import ProviderStatus, ProviderOffer
from app.core.logging import logger


class BaseProvider(ABC):
    """
    Abstract base class for all retailer and data collection providers.
    Enforces consistent health status reporting, URL routing, and fallback support.
    """

    def __init__(
        self,
        retailer_id: str,
        display_name: str,
        allowed_domains: List[str],
        status: ProviderStatus = ProviderStatus.PARTIAL,
        is_optional: bool = False,
    ):
        self.retailer_id = retailer_id
        self.display_name = display_name
        self.allowed_domains = [d.lower() for d in allowed_domains]
        self._status = status
        self.is_optional = is_optional

    @property
    def status(self) -> ProviderStatus:
        """Returns the current operational status of the adapter."""
        return self._status

    @status.setter
    def status(self, new_status: ProviderStatus) -> None:
        self._status = new_status

    def can_handle_url(self, url: str) -> bool:
        """Checks if this provider is responsible for the given URL domain."""
        if not url:
            return False
        try:
            parsed = urlparse(url)
            hostname = (parsed.hostname or "").lower()
            if not hostname:
                # Fallback check for URLs without scheme e.g. "amazon.in/dp/..."
                first_part = url.split("/")[0].lower()
                return any(first_part == d or first_part.endswith(f".{d}") for d in self.allowed_domains)
            return any(hostname == d or hostname.endswith(f".{d}") for d in self.allowed_domains)
        except Exception:
            return False

    def can_handle_query(self, query: str) -> bool:
        """Determines if query keywords are relevant to this provider."""
        if not query:
            return False
        return self.can_handle_url(query) or (self.retailer_id.lower() in query.lower())

    @abstractmethod
    def check_health(self) -> ProviderStatus:
        """Evaluates live availability, credential state, and network health."""
        pass

    @abstractmethod
    def fetch_and_extract(self, url: str) -> Optional[ProviderOffer]:
        """Fetches product URL and runs deterministic extraction pipeline."""
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 5) -> List[ProviderOffer]:
        """Executes a search query and returns normalized provider offers."""
        pass

    @abstractmethod
    def get_by_id(self, product_id: str) -> Optional[ProviderOffer]:
        """Retrieves offer by internal product ID or external SKU."""
        pass
