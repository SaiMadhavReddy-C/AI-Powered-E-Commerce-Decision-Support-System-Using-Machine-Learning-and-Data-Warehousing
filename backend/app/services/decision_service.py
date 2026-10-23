import datetime
from typing import Optional
from app.core.config import settings
from app.schemas.decision import DecisionSchema
from app.schemas.product import ProductDetailSchema, ProductAnalysisResponse
from app.schemas.offer import BestOfferSchema
from app.services.product_service import product_service
from app.core.logging import logger

from app.services.decision.synthesizer import decision_synthesizer


class DecisionService:
    """Evaluates product metrics, seller credentials, and pricing signals via ML & Decision Engine."""

    def __init__(self):
        self.model_version = settings.MODEL_VERSION
        self.rules_version = settings.DECISION_RULES_VERSION

    def evaluate_decision(self, product: ProductDetailSchema) -> DecisionSchema:
        """Constructs the strict DecisionSchema object utilizing live ML and safety gates."""
        return decision_synthesizer.synthesize(product)

    def analyze_product(self, product_or_query: str) -> ProductAnalysisResponse:
        """
        Main entry point for product analysis.
        Resolution order:
          1. Seeded catalog lookup by ID / alias
          2. URL / keyword heuristic resolver
          3. Gemini AI live resolution (for new queries not in catalog)
        """
        query = (product_or_query or "").strip()

        # Step 1: Direct catalog lookup
        product = product_service.get_by_id(query)

        # Step 2: URL / heuristic resolution
        if not product and (
            query.startswith("http://")
            or query.startswith("https://")
            or ".com" in query
            or ".in" in query
        ):
            product = product_service.resolve_by_url(query)

        # Step 3: Full resolution including Gemini AI for keyword searches
        if not product:
            logger.info(f"Catalog miss — escalating to resolve_new_product: '{query[:50]}'")
            product = product_service.resolve_new_product(query)

        # Ultimate fallback — return first seeded demo product
        if not product:
            logger.warning(f"All resolution paths failed for '{query[:50]}' — using demo fallback")
            product = product_service.get_all()[0]

        decision = self.evaluate_decision(product)

        return ProductAnalysisResponse(
            product=product,
            decision=decision,
            bestOffer=product.best_offer,
        )


decision_service = DecisionService()
