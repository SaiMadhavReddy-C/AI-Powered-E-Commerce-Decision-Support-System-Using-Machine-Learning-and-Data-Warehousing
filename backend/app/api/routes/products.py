from typing import List, Any
from fastapi import APIRouter, HTTPException, Path
from app.schemas.product import (
    ProductDetailSchema,
    ProductAnalysisResponse,
    PriceHistoryPointSchema,
)
from app.schemas.decision import DecisionSchema
from app.services.product_service import product_service
from app.services.decision_service import decision_service

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/{id}", response_model=ProductAnalysisResponse)
def get_product(id: str = Path(..., description="Product ID, alias, or encoded URL")):
    """
    GET /api/products/{id}
    Strict Contract:
    Returns { product, decision, best_offer }
    """
    product = product_service.get_by_id(id)
    if not product:
        product = product_service.resolve_by_url(id)

    if not product:
        raise HTTPException(status_code=404, detail=f"Product '{id}' not found")

    decision = decision_service.evaluate_decision(product)
    return ProductAnalysisResponse(
        product=product,
        decision=decision,
        bestOffer=product.best_offer,
    )

@router.get("/{id}/analysis", response_model=DecisionSchema)
def get_product_analysis(id: str = Path(..., description="Product ID or alias")):
    """
    GET /api/products/{id}/analysis
    Returns the strict decision breakdown for the product.
    """
    product = product_service.get_by_id(id)
    if not product:
        product = product_service.resolve_by_url(id)

    if not product:
        raise HTTPException(status_code=404, detail=f"Product '{id}' not found")

    return decision_service.evaluate_decision(product)

@router.get("/{id}/details", response_model=ProductDetailSchema)
def get_product_details(id: str = Path(..., description="Product ID or alias")):
    """
    GET /api/products/{id}/details
    Returns detailed product schema including 4-level identity entities.
    """
    product = product_service.get_by_id(id)
    if not product:
        product = product_service.resolve_by_url(id)

    if not product:
        raise HTTPException(status_code=404, detail=f"Product '{id}' not found")

    return product

@router.get("/{id}/offers", response_model=List[Any])
def get_product_offers(id: str = Path(..., description="Product ID or alias")):
    """
    GET /api/products/{id}/offers
    Returns all active retailer listings, competitor offers, and best offer options.
    """
    product = product_service.get_by_id(id)
    if not product:
        product = product_service.resolve_by_url(id)

    if not product:
        raise HTTPException(status_code=404, detail=f"Product '{id}' not found")

    return product_service.get_offers(product.id)

@router.get("/{id}/price-history", response_model=List[PriceHistoryPointSchema])
def get_product_price_history(id: str = Path(..., description="Product ID or alias")):
    """
    GET /api/products/{id}/price-history
    Returns historical price points with timestamps and shipping costs.
    """
    product = product_service.get_by_id(id)
    if not product:
        product = product_service.resolve_by_url(id)

    if not product:
        raise HTTPException(status_code=404, detail=f"Product '{id}' not found")

    return product_service.get_price_history(product.id)
