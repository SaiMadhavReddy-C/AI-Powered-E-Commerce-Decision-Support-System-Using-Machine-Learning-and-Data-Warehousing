from fastapi import APIRouter, Body
from app.schemas.preferences import PreferencesSchema
from app.services.preferences_service import preferences_service

router = APIRouter(prefix="/preferences", tags=["Preferences"])

@router.get("", response_model=PreferencesSchema)
def get_user_preferences():
    """
    GET /api/preferences
    Retrieves the current shopping criteria and notification channel settings.
    """
    return preferences_service.get_preferences()

@router.put("", response_model=PreferencesSchema)
def update_user_preferences(payload: PreferencesSchema = Body(...)):
    """
    PUT /api/preferences
    Updates shopping priority, wait tolerance, and notification channels.
    """
    return preferences_service.update_preferences(payload)
