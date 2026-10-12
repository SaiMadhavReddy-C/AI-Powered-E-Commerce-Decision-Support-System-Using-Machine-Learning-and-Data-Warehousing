from typing import Optional, Union
from pydantic import BaseModel, Field

class AlertSchema(BaseModel):
    id: Union[int, str]
    title: str
    message: str
    timestamp: str
    read: bool = False
    product_id: Optional[str] = Field(default=None, alias="productId")

    class Config:
        populate_by_name = True

class AlertMarkReadResponse(BaseModel):
    success: bool = True
    alert_id: Union[int, str] = Field(..., alias="alertId")
    read: bool = True
    message: Optional[str] = "Alert marked as read"

    class Config:
        populate_by_name = True
