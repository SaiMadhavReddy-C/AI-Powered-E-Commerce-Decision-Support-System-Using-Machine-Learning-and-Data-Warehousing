from typing import Optional
from pydantic import BaseModel, Field

class NotificationSettingsSchema(BaseModel):
    price_drops: bool = Field(default=True, alias="priceDrops")
    seller_warnings: bool = Field(default=True, alias="sellerWarnings")
    upcoming_sales: bool = Field(default=True, alias="upcomingSales")
    daily_digest: bool = Field(default=False, alias="dailyDigest")

    class Config:
        populate_by_name = True

class PreferencesSchema(BaseModel):
    primary_priority: str = Field(default="best_price", alias="primaryPriority")
    wait_tolerance: str = Field(default="moderate", alias="waitTolerance")
    notifications: NotificationSettingsSchema = Field(default_factory=NotificationSettingsSchema)
    notification_channel: str = Field(default="in_app", alias="notificationChannel")
    email: Optional[str] = Field(default="")

    class Config:
        populate_by_name = True
