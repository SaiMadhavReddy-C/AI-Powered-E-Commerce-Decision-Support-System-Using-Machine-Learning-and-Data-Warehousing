from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health")
def get_health():
    """Health check endpoint to verify backend operational readiness."""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
    }
