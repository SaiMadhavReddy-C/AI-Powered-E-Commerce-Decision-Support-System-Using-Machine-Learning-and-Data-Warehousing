from fastapi import APIRouter, Body, HTTPException
from app.schemas.analyze import AnalyzeRequest
from app.schemas.product import ProductAnalysisResponse
from app.services.decision_service import decision_service

router = APIRouter(prefix="/analyze", tags=["Analyze"])

@router.post("", response_model=ProductAnalysisResponse)
def analyze_product_endpoint(payload: AnalyzeRequest = Body(...)):
    """
    POST /api/analyze
    Analyzes input URL, product ID, or search query.
    Strict Contract:
    Returns { product, decision, best_offer }
    """
    query = payload.get_query()
    analysis = decision_service.analyze_product(query)
    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="No verified price found. Paste a supported retailer product link to check its current price.",
        )
    return analysis
