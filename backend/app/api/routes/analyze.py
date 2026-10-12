from fastapi import APIRouter, Body
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
    return decision_service.analyze_product(query)
