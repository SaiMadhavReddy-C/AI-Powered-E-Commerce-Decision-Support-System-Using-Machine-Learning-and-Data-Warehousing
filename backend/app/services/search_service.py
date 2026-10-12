from typing import List
from app.schemas.product import ProductDetailSchema
from app.schemas.search import SearchResponse
from app.services.product_service import product_service

class SearchService:
    """Service providing search and product discovery algorithms."""

    def search(self, query: str, limit: int = 20) -> SearchResponse:
        """Executes search by keyword query or resolves directly if query is a URL."""
        if not query or not query.strip():
            all_products = product_service.get_all()[:limit]
            return SearchResponse(query="", total=len(all_products), results=all_products)

        trimmed = query.strip()
        lower = trimmed.lower()

        # If input looks like a URL or domain
        if (
            trimmed.startswith("http://")
            or trimmed.startswith("https://")
            or ".com" in trimmed
            or ".in" in trimmed
        ):
            resolved = product_service.resolve_by_url(trimmed)
            return SearchResponse(query=trimmed, total=1, results=[resolved])

        # Filter products by token matching
        all_products = product_service.get_all()
        matches: List[ProductDetailSchema] = []

        tokens = lower.split()
        for p in all_products:
            searchable_text = f"{p.name} {p.brand or ''} {p.category or ''} {p.variant or ''} {p.id}".lower()
            if any(t in searchable_text for t in tokens):
                matches.append(p)

        # Attempt dynamic resolution if no existing catalog item matches
        if not matches:
            resolved_new = product_service.resolve_new_product(trimmed)
            if resolved_new:
                matches = [resolved_new]

        limited = matches[:limit]
        return SearchResponse(query=query, total=len(limited), results=limited)


search_service = SearchService()
