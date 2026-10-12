from typing import Optional
from fastapi import APIRouter, Query, Body
from app.schemas.search import SearchRequest, SearchResponse
from app.services.search_service import search_service

router = APIRouter(prefix="/search", tags=["Search"])

@router.post("", response_model=SearchResponse)
def search_products(
    payload: Optional[SearchRequest] = Body(default=None),
    q: Optional[str] = Query(default=None, description="Optional query parameter fallback"),
):
    """
    POST /api/search
    Searches products by keyword, category, brand, or resolves a product directly from URL.
    """
    query = (payload.query if payload and payload.query else "") or (q or "")
    limit = payload.limit if payload and payload.limit else 20
    return search_service.search(query=query, limit=limit)
