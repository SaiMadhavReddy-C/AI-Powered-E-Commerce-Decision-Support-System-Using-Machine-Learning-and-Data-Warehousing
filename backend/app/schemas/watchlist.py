from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.product import ProductDetailSchema

class WatchlistCreateRequest(BaseModel):
    product_id: str = Field(..., alias="productId", description="Product ID to track")
    target_price: Optional[float] = Field(default=None, alias="targetPrice", description="User target alert price")

    class Config:
        populate_by_name = True

class WatchlistStatusSchema(BaseModel):
    emoji: Optional[str] = "👀"
    icon: Optional[str] = "👀"
    message: str = "Monitoring prices"
    type: Optional[str] = "neutral"

    class Config:
        populate_by_name = True

class WatchlistItemSchema(ProductDetailSchema):
    target_price: Optional[float] = Field(default=None, alias="targetPrice")
    watch_group: Optional[str] = Field(default="WATCHING", alias="watchGroup")
    watch_message: Optional[str] = Field(default=None, alias="watchMessage")
    watch_status: Optional[WatchlistStatusSchema] = Field(default=None, alias="watchStatus")
    action_label: Optional[str] = Field(default="Check now", alias="actionLabel")
    last_checked_text: Optional[str] = Field(default="Checked just now", alias="lastCheckedText")

    class Config:
        populate_by_name = True

class WatchlistDeleteResponse(BaseModel):
    success: bool = True
    product_id: str = Field(..., alias="productId")
    message: Optional[str] = "Item removed from watchlist"

    class Config:
        populate_by_name = True
