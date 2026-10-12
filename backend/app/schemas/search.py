from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.product import ProductDetailSchema

class SearchRequest(BaseModel):
    query: str = Field(default="", description="Search query keyword, title, or product URL")
    limit: Optional[int] = Field(default=20, description="Max search results count")

class SearchResponse(BaseModel):
    query: str
    total: int
    results: List[ProductDetailSchema]

    class Config:
        populate_by_name = True
