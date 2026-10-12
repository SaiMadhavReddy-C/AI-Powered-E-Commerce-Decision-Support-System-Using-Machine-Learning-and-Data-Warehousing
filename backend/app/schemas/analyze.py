from typing import Optional
from pydantic import BaseModel, Field

class AnalyzeRequest(BaseModel):
    """Input payload for POST /api/analyze."""
    input: Optional[str] = Field(default=None, description="URL or product name/query to analyze")
    url: Optional[str] = Field(default=None, description="Direct product URL")
    product_id: Optional[str] = Field(default=None, alias="productId", description="Product ID or alias")

    def get_query(self) -> str:
        """Helper to extract non-empty query string from any provided field."""
        if self.url and self.url.strip():
            return self.url.strip()
        if self.input and self.input.strip():
            return self.input.strip()
        if self.product_id and self.product_id.strip():
            return self.product_id.strip()
        return ""

    class Config:
        populate_by_name = True
