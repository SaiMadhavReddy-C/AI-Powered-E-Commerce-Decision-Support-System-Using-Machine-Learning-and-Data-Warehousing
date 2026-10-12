from typing import List
from fastapi import APIRouter, HTTPException, Path, Body
from app.schemas.watchlist import (
    WatchlistItemSchema,
    WatchlistCreateRequest,
    WatchlistDeleteResponse,
)
from app.services.watchlist_service import watchlist_service

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])

@router.get("", response_model=List[WatchlistItemSchema])
def get_watchlist():
    """
    GET /api/watchlist
    Returns the user's active tracked items and recommendation alerts.
    """
    return watchlist_service.get_all()

@router.post("", response_model=WatchlistItemSchema)
def add_to_watchlist(payload: WatchlistCreateRequest = Body(...)):
    """
    POST /api/watchlist
    Adds a product to the user's watchlist with an optional target alert price.
    """
    return watchlist_service.add(
        product_id=payload.product_id,
        target_price=payload.target_price,
    )

@router.delete("/{id}", response_model=WatchlistDeleteResponse)
def remove_from_watchlist(id: str = Path(..., description="Product ID to remove from watchlist")):
    """
    DELETE /api/watchlist/{id}
    Removes a product from the user's watchlist.
    """
    success = watchlist_service.delete(id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Item '{id}' not found in watchlist")

    return WatchlistDeleteResponse(success=True, productId=id)
