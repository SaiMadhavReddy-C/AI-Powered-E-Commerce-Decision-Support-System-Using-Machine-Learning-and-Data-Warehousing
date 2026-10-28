from fastapi import APIRouter, Body, HTTPException

from app.schemas.notification import TestEmailRequest
from app.services.email_service import email_service

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("/test-email")
def send_test_email(payload: TestEmailRequest = Body(...)):
    try:
        result = email_service.send(
            recipient=payload.recipient,
            subject="ShopQ email notifications are connected",
            html="<p>Your ShopQ email notification settings are working.</p>",
            text="Your ShopQ email notification settings are working.",
        )
        return {"success": True, "id": result.get("id"), "status": result.get("status")}
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
