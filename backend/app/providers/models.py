"""Data models, enums, and schemas for ShopQ Provider and Extraction system."""

import datetime
from enum import Enum
from typing import Optional, Union, List, Dict, Any
from pydantic import BaseModel, Field

from app.schemas.offer import SellerSchema, BestOfferSchema, CompetitorOfferSchema
from app.schemas.product import (
    ProductDetailSchema,
    CanonicalProductSchema,
    CanonicalVariantSchema,
    RetailerListingSchema,
    SellerOfferSchema,
    PriceHistoryPointSchema,
)


class ProviderStatus(str, Enum):
    """Operational status of a retailer or data provider adapter."""
    LIVE = "LIVE"
    PARTIAL = "PARTIAL"
    MOCK = "MOCK"
    UNAVAILABLE = "UNAVAILABLE"


class ExtractionStage(str, Enum):
    """The pipeline stage that resolved the product data."""
    JSON_LD = "JSON_LD"
    KNOWN_SELECTORS = "KNOWN_SELECTORS"
    GENERIC_DOM = "GENERIC_DOM"
    REGEX_NORMALIZATION = "REGEX_NORMALIZATION"
    LLM_FALLBACK = "LLM_FALLBACK"
    MOCK_DATA = "MOCK_DATA"


class ConfidenceLevel(str, Enum):
    """Confidence grade for extraction and data accuracy."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNCERTAIN = "UNCERTAIN"


class ProviderOffer(BaseModel):
    """
    Normalized offer schema returned by all provider adapters and extraction stages.
    Guarantees strict type consistency across live scrapers and mock providers.
    """
    retailer: str = Field(..., description="Canonical retailer key (e.g. amazon, flipkart, croma)")
    retailer_name: str = Field(..., description="Human-readable retailer name (e.g. Amazon, Flipkart)")
    product_title: str = Field(..., description="Normalized product title")
    brand: Optional[str] = Field(default=None, description="Extracted brand name")
    model: Optional[str] = Field(default=None, description="Model number or spec")
    variant: Optional[str] = Field(default=None, description="Variant name, color, or capacity")
    category: Optional[str] = Field(default="Electronics", description="Product category")
    price: float = Field(..., description="Current offer price in specified currency")
    currency: str = Field(default="INR", description="Currency ISO code (INR default)")
    original_price: Optional[float] = Field(default=None, description="MRP or original listed price")
    discount_percentage: Optional[float] = Field(default=None, description="Calculated or listed discount %")
    seller: Union[SellerSchema, Dict[str, Any], str] = Field(..., description="Seller details or seller name")
    seller_name: str = Field(..., description="Normalized merchant/seller name")
    rating: Optional[float] = Field(default=4.5, description="Product or seller rating")
    review_count: Optional[int] = Field(default=1000, description="Total review count")
    availability: str = Field(default="IN_STOCK", description="Stock availability status: IN_STOCK, OUT_OF_STOCK, LIMITED_STOCK")
    shipping: Optional[str] = Field(default="Free Delivery", description="Shipping description")
    shipping_cost: float = Field(default=0.0, description="Shipping cost in INR")
    image_url: Optional[str] = Field(default=None, description="Product image URL")
    product_url: str = Field(..., description="Canonical URL to the retailer product listing")
    observed_at: str = Field(..., description="ISO timestamp when price was observed on webpage")
    collected_at: str = Field(..., description="ISO timestamp when observation was stored")
    source_type: str = Field(default="SCRAPERAPI", description="Origin: SCRAPERAPI, MOCK, DIRECT")
    source_status: str = Field(default="LIVE", description="Status at collection: LIVE, PARTIAL, MOCK, UNAVAILABLE")
    confidence_score: float = Field(default=0.95, description="Confidence score between 0.0 and 1.0")
    uncertain_fields: List[str] = Field(default_factory=list, description="Fields flagged as ambiguous or uncertain")
    extraction_stage: str = Field(default="JSON_LD", description="Pipeline stage that extracted this offer")
    raw_metadata: Dict[str, Any] = Field(default_factory=dict, description="Diagnostic and provider metadata")

    class Config:
        populate_by_name = True

    def get_seller_schema(self) -> SellerSchema:
        """Coerces seller into a validated SellerSchema."""
        if isinstance(self.seller, SellerSchema):
            return self.seller
        if isinstance(self.seller, dict):
            return SellerSchema(
                name=self.seller.get("name", self.seller_name),
                rating=float(self.seller.get("rating", self.rating or 4.5)),
                reviews=int(self.seller.get("reviews", self.review_count or 1000)),
                reviewCount=int(self.seller.get("reviewCount", self.review_count or 1000)),
                reliability=self.seller.get("reliability", "RELIABLE"),
                returnPolicy=self.seller.get("returnPolicy", "7-day replacement"),
                warranty=self.seller.get("warranty", "1 year manufacturer"),
            )
        return SellerSchema(
            name=str(self.seller or self.seller_name),
            rating=self.rating or 4.5,
            reviews=self.review_count or 1000,
            reviewCount=self.review_count or 1000,
            reliability="RELIABLE",
            returnPolicy="7-day replacement",
            warranty="1 year manufacturer",
        )

    def to_best_offer(self, savings: float = 0.0) -> BestOfferSchema:
        """Converts to BestOfferSchema for API response."""
        return BestOfferSchema(
            id=f"bo_{self.retailer.lower()}_{abs(hash(self.product_url)) % 1000000}",
            retailer=self.retailer_name,
            price=self.price,
            seller=self.get_seller_schema(),
            isReliable=self.get_seller_schema().reliability in ("RELIABLE", "HIGH"),
            inStock=self.availability == "IN_STOCK",
            available=self.availability != "OUT_OF_STOCK",
            url=self.product_url,
            savings=savings,
        )

    def to_competitor_offer(self) -> CompetitorOfferSchema:
        """Converts to CompetitorOfferSchema for comparison matrices."""
        return CompetitorOfferSchema(
            retailer=self.retailer.lower(),
            seller=self.seller_name,
            price=self.price,
            isReliable=self.get_seller_schema().reliability in ("RELIABLE", "HIGH"),
            available=self.availability != "OUT_OF_STOCK",
            inStock=self.availability == "IN_STOCK",
            url=self.product_url,
        )

    def to_product_detail(
        self,
        id: Optional[str] = None,
        product_id: Optional[str] = None,
        recommendation: str = "BUY",
        confidence: str = "HIGH",
        explanation: str = "Extracted from verified retail listing.",
        reasons: Optional[List[str]] = None,
        buy_point: Optional[float] = None,
        trend: str = "STABLE",
        data_status: str = "LIVE",
        price_history: Optional[List[PriceHistoryPointSchema]] = None,
        competitors: Optional[List[CompetitorOfferSchema]] = None,
    ) -> ProductDetailSchema:
        """Transforms the ProviderOffer into a complete 4-level ProductDetailSchema."""
        pid = id or product_id or f"prod_{self.retailer}_{abs(hash(self.product_url)) % 1000000}"
        seller_obj = self.get_seller_schema()

        cp = CanonicalProductSchema(
            id=f"cp_{pid}",
            name=self.product_title,
            title=self.product_title,
            brand=self.brand or "Generic",
            category=self.category or "Electronics",
            model=self.model or self.product_title,
            description=explanation,
        )

        cv = CanonicalVariantSchema(
            id=f"cv_{pid}_std",
            productId=cp.id,
            variant=self.variant or "Standard",
            color=self.variant or "Standard",
            sku=f"SKU-{pid.upper()}",
            image=self.image_url or "https://placehold.co/300x300/FAF8F5/1A1A1A?text=ShopQ",
        )

        rl = RetailerListingSchema(
            id=f"rl_{self.retailer}_{pid}",
            variantId=cv.id,
            retailer=self.retailer,
            retailerName=self.retailer_name,
            url=self.product_url,
            listingSku=f"LST-{pid.upper()}",
            availabilityStatus=self.availability,
        )

        so = SellerOfferSchema(
            id=f"so_{self.retailer}_{pid}",
            listingId=rl.id,
            sellerId=f"seller_{self.seller_name.lower().replace(' ', '_')}",
            sellerName=seller_obj.name,
            price=self.price,
            currency=self.currency,
            shippingCost=self.shipping_cost,
            availabilityStatus=self.availability,
            rating=seller_obj.rating,
            reviews=seller_obj.reviews,
            reviewCount=seller_obj.review_count,
            reliability=seller_obj.reliability,
            returnPolicy=seller_obj.return_policy,
            warranty=seller_obj.warranty,
        )

        return ProductDetailSchema(
            id=pid,
            name=self.product_title,
            brand=self.brand or "Generic",
            category=self.category or "Electronics",
            variant=self.variant or "Standard",
            image=self.image_url or "https://placehold.co/300x300/FAF8F5/1A1A1A?text=ShopQ",
            currentPrice=self.price,
            retailer=self.retailer,
            retailerUrl=self.product_url,
            seller=seller_obj,
            recommendation=recommendation,
            confidence=confidence,
            explanation=explanation,
            reasons=reasons or [
                f"Current live offer is ₹{self.price:,.0f} on {self.retailer_name}",
                f"Merchant {seller_obj.name} verified with {seller_obj.rating}★ rating",
            ],
            buyPoint=buy_point or self.price,
            trend=trend,
            historicalLow=self.original_price or self.price,
            historicalHigh=self.original_price or self.price,
            lastChecked=self.collected_at,
            dataStatus=data_status,
            priceHistory=price_history or [],
            competitors=competitors or [],
            bestOffer=self.to_best_offer(),
            canonical_product=cp,
            canonical_variant=cv,
            retailer_listing=rl,
            seller_offer=so,
        )
