from typing import List, Union
from fastapi import APIRouter, HTTPException, Path
from app.schemas.alert import AlertSchema, AlertMarkReadResponse
from app.services.alert_service import alert_service

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("", response_model=List[AlertSchema])
def get_alerts():
    """
    GET /api/alerts
    Returns all notifications including price drops, seller warnings, and sale events.
    """
    return alert_service.get_all()

@router.post("/{id}/read", response_model=AlertMarkReadResponse)
def mark_alert_as_read(id: Union[int, str] = Path(..., description="Alert ID to mark read")):
    """
    POST /api/alerts/{id}/read
    Marks a notification alert as read.
    """
    alert = alert_service.mark_as_read(id)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert '{id}' not found")

    return AlertMarkReadResponse(success=True, alertId=id, read=True)
