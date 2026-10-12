import threading
from app.schemas.preferences import PreferencesSchema, NotificationSettingsSchema

class PreferencesService:
    """Manages user shopping strategy and notification preferences."""

    def __init__(self):
        self._lock = threading.Lock()
        self._preferences = PreferencesSchema(
            primaryPriority="best_price",
            waitTolerance="moderate",
            notifications=NotificationSettingsSchema(
                priceDrops=True,
                sellerWarnings=True,
                upcomingSales=True,
                dailyDigest=False,
            ),
            notificationChannel="in_app",
            email="",
        )

    def get_preferences(self) -> PreferencesSchema:
        """Returns current active preferences."""
        with self._lock:
            return self._preferences.model_copy()

    def update_preferences(self, new_pref: PreferencesSchema) -> PreferencesSchema:
        """Updates and stores user preferences."""
        with self._lock:
            self._preferences = new_pref.model_copy()
            return self._preferences.model_copy()


preferences_service = PreferencesService()
