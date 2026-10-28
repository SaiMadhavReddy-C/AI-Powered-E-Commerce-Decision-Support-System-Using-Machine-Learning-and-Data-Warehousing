from fastapi import APIRouter, Body, HTTPException

from app.schemas.auth import OtpRequest, OtpVerifyRequest
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/request-otp")
def request_otp(payload: OtpRequest = Body(...)):
    if "@" not in payload.email:
        raise HTTPException(status_code=422, detail="Enter a valid email address")
    try:
        return auth_service.request_otp(payload.email)
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


@router.post("/verify-otp")
def verify_otp(payload: OtpVerifyRequest = Body(...)):
    token = auth_service.verify_otp(payload.email, payload.code)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid or expired code")
    return {"token": token, "email": payload.email.strip().lower()}
