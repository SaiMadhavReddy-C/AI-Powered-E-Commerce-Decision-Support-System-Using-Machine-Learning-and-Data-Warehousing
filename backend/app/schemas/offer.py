from typing import Optional, Union, Any, Dict
from pydantic import BaseModel, Field

class SellerSchema(BaseModel):
    name: str = Field(..., description="Seller merchant name")
    rating: Optional[float] = Field(default=4.5, description="Average seller rating out of 5")
    reviews: Optional[int] = Field(default=1000, description="Total review count")
    review_count: Optional[int] = Field(default=1000, alias="reviewCount")
    reliability: Optional[str] = Field(default="RELIABLE", description="Reliability grade: RELIABLE, MODERATE, RISKY, UNKNOWN")
    return_policy: Optional[str] = Field(default="7-day replacement", alias="returnPolicy")
    warranty: Optional[str] = Field(default="1 year manufacturer")

    class Config:
        populate_by_name = True

class BestOfferSchema(BaseModel):
    id: Optional[str] = Field(default=None, description="Offer identifier")
    retailer: str = Field(..., description="Retailer or platform name (e.g. Myntra, Amazon)")
    price: float = Field(..., description="Current offer price")
    seller: Optional[Union[SellerSchema, Dict[str, Any], str]] = Field(default=None, description="Seller details or seller name")
    is_reliable: bool = Field(default=True, alias="isReliable")
    in_stock: bool = Field(default=True, alias="inStock")
    available: bool = Field(default=True)
    url: Optional[str] = Field(default=None, description="Direct URL to offer")
    savings: Optional[float] = Field(default=0.0, description="Estimated savings compared to baseline")

    class Config:
        populate_by_name = True

class CompetitorOfferSchema(BaseModel):
    retailer: str = Field(..., description="Competitor retailer name")
    seller: Optional[Union[str, SellerSchema, Dict[str, Any]]] = Field(default="Verified Store")
    price: float = Field(..., description="Competitor offer price")
    is_reliable: bool = Field(default=True, alias="isReliable")
    available: bool = Field(default=True)
    in_stock: bool = Field(default=True, alias="inStock")
    url: Optional[str] = Field(default=None)

    class Config:
        populate_by_name = True
