from app.schemas.search import SearchResponse
from app.services.product_service import product_service
from app.providers.registry import provider_registry

class SearchService:
    """Service providing search and product discovery algorithms."""

    def search(self, query: str, limit: int = 20) -> SearchResponse:
        """Executes search by keyword query or resolves directly if query is a URL."""
        if not query or not query.strip():
            return SearchResponse(query="", total=0, results=[])

        trimmed = query.strip()
        # If input looks like a URL or domain
        if (
            trimmed.startswith("http://")
            or trimmed.startswith("https://")
            or ".com" in trimmed
            or ".in" in trimmed
        ):
            resolved = product_service.resolve_by_url(trimmed)
            return SearchResponse(
                query=trimmed,
                total=1 if resolved else 0,
                results=[resolved] if resolved else [],
            )

        offers = provider_registry.search(trimmed, limit=limit)
        products = [
            offer.to_product_detail(
                explanation="Price extracted from a verified retailer result.",
                reasons=["Price was checked on the retailer listing."],
                confidence="MEDIUM",
            )
            for offer in offers
        ]
        return SearchResponse(query=query, total=len(products), results=products)


search_service = SearchService()
