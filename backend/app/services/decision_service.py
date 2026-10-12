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
        """Constructs the strict DecisionSchema object for a given product utilizing live ML and safety gates."""
        return decision_synthesizer.synthesize(product)

    def analyze_product(self, product_or_query: str) -> ProductAnalysisResponse:
        """
        Main entry point for product analysis.
        Accepts ID, URL, or search query, resolves the product, and returns the strict contract.
        """
        product = product_service.get_by_id(product_or_query)
        if not product:
            # Fall back to URL resolution or default demo item
            product = product_service.resolve_by_url(product_or_query)

        decision = self.evaluate_decision(product)

        return ProductAnalysisResponse(
            product=product,
            decision=decision,
            bestOffer=product.best_offer,
        )


decision_service = DecisionService()
