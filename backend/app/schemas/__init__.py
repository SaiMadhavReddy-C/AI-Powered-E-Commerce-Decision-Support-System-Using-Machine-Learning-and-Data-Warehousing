"""Pydantic schemas for request and response validation."""

from app.schemas.decision import DecisionSchema
from app.schemas.offer import BestOfferSchema, CompetitorOfferSchema, SellerSchema
from app.schemas.product import (
    ProductDetailSchema,
    ProductAnalysisResponse,
    PriceHistoryPointSchema,
    CanonicalProductSchema,
    CanonicalVariantSchema,
    RetailerListingSchema,
    SellerOfferSchema,
)
from app.schemas.watchlist import WatchlistItemSchema, WatchlistCreateRequest, WatchlistDeleteResponse
from app.schemas.alert import AlertSchema, AlertMarkReadResponse
from app.schemas.preferences import PreferencesSchema
from app.schemas.search import SearchRequest, SearchResponse
from app.schemas.analyze import AnalyzeRequest

__all__ = [
    "DecisionSchema",
    "BestOfferSchema",
    "CompetitorOfferSchema",
    "SellerSchema",
    "ProductDetailSchema",
    "ProductAnalysisResponse",
    "PriceHistoryPointSchema",
    "CanonicalProductSchema",
    "CanonicalVariantSchema",
    "RetailerListingSchema",
    "SellerOfferSchema",
    "WatchlistItemSchema",
    "WatchlistCreateRequest",
    "WatchlistDeleteResponse",
    "AlertSchema",
    "AlertMarkReadResponse",
    "PreferencesSchema",
    "SearchRequest",
    "SearchResponse",
    "AnalyzeRequest",
]
