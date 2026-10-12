from typing import List, Optional
from pydantic import BaseModel, Field

class DecisionSchema(BaseModel):
    """
    Strict Decision schema conforming to the ShopQ API Contract:
    - decision: BUY | WAIT | CAUTION | CHECK_ALT | NO_DECISION | YOUR_CALL | DONT_RUSH | WAIT_SALE | GRAB
    - confidence_level: HIGH | MEDIUM | LOW
    - primary_reason: Clear 1-sentence reasoning
    - secondary_reasons: Supporting bullet points
    - buy_point: Target price or None
    - best_offer_id: ID of the best offer or None
    - data_freshness: FRESH | RECENT | STALE
    - data_coverage: Coverage metric (e.g., '98%')
    - checked_at: ISO timestamp of evaluation
    - model_version: Decision engine model identifier
    - decision_rules_version: Version of ruleset applied
    """
    decision: str = Field(..., description="Actionable recommendation: BUY, WAIT, CAUTION, CHECK_ALT, etc.")
    confidence_level: str = Field(..., description="Confidence level: HIGH, MEDIUM, LOW")
    primary_reason: str = Field(..., description="Primary explanatory rationale for the decision")
    secondary_reasons: List[str] = Field(default_factory=list, description="Secondary factors and supporting observations")
    buy_point: Optional[float] = Field(default=None, description="Recommended purchase price threshold")
    best_offer_id: Optional[str] = Field(default=None, description="Identifier of the recommended best offer if available")
    data_freshness: str = Field(default="FRESH", description="Freshness of scraped signals: FRESH, RECENT, STALE")
    data_coverage: str = Field(default="98%", description="Coverage percentage of verified market signals")
    checked_at: str = Field(..., description="ISO 8601 timestamp of evaluation")
    model_version: str = Field(default="shopq-decision-v2.1", description="Model engine version")
    decision_rules_version: str = Field(default="rules-2026.10", description="Ruleset version")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "decision": "BUY",
                "confidence_level": "HIGH",
                "primary_reason": "Lowest price recorded in 90 days from an authorized seller.",
                "secondary_reasons": [
                    "Price dropped ₹3,500 today to ₹22,499",
                    "Top-rated seller Appario Retail (4.8★)",
                    "Competitors are priced ₹2,500+ higher"
                ],
                "buy_point": 23999.0,
                "best_offer_id": "so_appario_retail_sony_good_deal",
                "data_freshness": "FRESH",
                "data_coverage": "98%",
                "checked_at": "2026-10-07T18:00:00Z",
                "model_version": "shopq-decision-v2.1",
                "decision_rules_version": "rules-2026.10"
            }
        }
