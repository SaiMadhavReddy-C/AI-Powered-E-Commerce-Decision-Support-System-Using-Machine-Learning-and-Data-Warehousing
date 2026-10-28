from typing import List, Optional, Any, Dict, Union
from pydantic import BaseModel, Field
from app.schemas.decision import DecisionSchema
from app.schemas.offer import BestOfferSchema, CompetitorOfferSchema, SellerSchema

class PriceHistoryPointSchema(BaseModel):
    date: Optional[str] = None
    observed_at: Optional[str] = None
    collected_at: Optional[str] = None
    price: float
    shipping_cost: Optional[float] = Field(default=0.0, alias="shippingCost")
    availability_status: Optional[str] = Field(default="IN_STOCK", alias="availabilityStatus")

    class Config:
        populate_by_name = True

class CanonicalProductSchema(BaseModel):
    id: str
    name: str
    title: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    model: Optional[str] = None
    description: Optional[str] = None

    class Config:
        populate_by_name = True

class CanonicalVariantSchema(BaseModel):
    id: str
    product_id: Optional[str] = Field(default=None, alias="productId")
    variant: Optional[str] = None
    color: Optional[str] = None
    sku: Optional[str] = None
    image: Optional[str] = None

    class Config:
        populate_by_name = True

class RetailerListingSchema(BaseModel):
    id: str
    variant_id: Optional[str] = Field(default=None, alias="variantId")
    retailer: Optional[str] = None
    retailer_name: Optional[str] = Field(default=None, alias="retailerName")
    url: Optional[str] = None
    listing_sku: Optional[str] = Field(default=None, alias="listingSku")
    availability_status: Optional[str] = Field(default="IN_STOCK", alias="availabilityStatus")

    class Config:
        populate_by_name = True

class SellerOfferSchema(BaseModel):
    id: str
    listing_id: Optional[str] = Field(default=None, alias="listingId")
    seller_id: Optional[str] = Field(default=None, alias="sellerId")
    seller_name: Optional[str] = Field(default=None, alias="sellerName")
    price: float
    currency: Optional[str] = "INR"
    shipping_cost: Optional[float] = Field(default=0.0, alias="shippingCost")
    availability_status: Optional[str] = Field(default="IN_STOCK", alias="availabilityStatus")
    rating: Optional[float] = 4.5
    reviews: Optional[int] = 1000
    review_count: Optional[int] = Field(default=1000, alias="reviewCount")
    reliability: Optional[str] = "RELIABLE"
    return_policy: Optional[str] = Field(default="7-day replacement", alias="returnPolicy")
    warranty: Optional[str] = "1 year manufacturer"

    class Config:
        populate_by_name = True

class ProductDetailSchema(BaseModel):
    id: str
    name: str
    brand: Optional[str] = None
    category: Optional[str] = None
    variant: Optional[str] = None
    image: Optional[str] = None
    current_price: float = Field(..., alias="currentPrice")
    retailer: Optional[str] = None
    retailer_url: Optional[str] = Field(default=None, alias="retailerUrl")
    seller: Optional[Union[SellerSchema, Dict[str, Any]]] = None
    recommendation: Optional[str] = "BUY"
    confidence: Optional[str] = "HIGH"
    explanation: Optional[str] = ""
    reasons: List[str] = Field(default_factory=list)
    buy_point: Optional[float] = Field(default=None, alias="buyPoint")
    trend: Optional[str] = "STABLE"
    historical_low: Optional[float] = Field(default=None, alias="historicalLow")
    historical_high: Optional[float] = Field(default=None, alias="historicalHigh")
    last_checked: Optional[str] = Field(default=None, alias="lastChecked")
    data_status: str = Field(default="LIVE", alias="dataStatus")
    price_history: List[PriceHistoryPointSchema] = Field(default_factory=list, alias="priceHistory")
    competitors: List[CompetitorOfferSchema] = Field(default_factory=list)
    best_offer: Optional[BestOfferSchema] = Field(default=None, alias="bestOffer")

    # 4-Level Schema
    canonical_product: Optional[CanonicalProductSchema] = None
    canonical_variant: Optional[CanonicalVariantSchema] = None
    retailer_listing: Optional[RetailerListingSchema] = None
    seller_offer: Optional[SellerOfferSchema] = None

    class Config:
        populate_by_name = True

class ProductAnalysisResponse(BaseModel):
    """
    Strict API Contract for /api/analyze and /api/products/{id}
    Returns:
    - product: ProductDetailSchema
    - decision: DecisionSchema
    - best_offer: Optional[BestOfferSchema]
    """
    product: ProductDetailSchema
    decision: DecisionSchema
    best_offer: Optional[BestOfferSchema] = Field(default=None, alias="bestOffer")

    class Config:
        populate_by_name = True
