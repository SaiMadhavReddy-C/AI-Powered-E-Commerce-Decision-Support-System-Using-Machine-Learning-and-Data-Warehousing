import threading
import datetime
from typing import List, Optional, Union, Dict
from app.schemas.alert import AlertSchema
from app.core.config import settings

class AlertService:
    """Manages price and seller change alerts for tracked products."""

    def __init__(self):
        self._lock = threading.Lock()
        self._alerts: Dict[str, AlertSchema] = {}
        self._init_seed_alerts()

    def _init_seed_alerts(self):
        if settings.IS_PRODUCTION:
            return
        now = datetime.datetime.now(datetime.timezone.utc)
        a1 = AlertSchema(
            id=1,
            title="Price Drop Alert",
            message="Apple iPhone 15 has dropped to your target price of ₹54,999.",
            timestamp=(now - datetime.timedelta(minutes=30)).isoformat(),
            read=False,
            productId="iphone_wait",
        )
        a2 = AlertSchema(
            id=2,
            title="Seller Warning",
            message="The default seller for HP Pavilion 14 has changed to a lower-rated seller.",
            timestamp=(now - datetime.timedelta(hours=2)).isoformat(),
            read=True,
            productId="laptop_suspicious_seller",
        )
        a3 = AlertSchema(
            id=3,
            title="Sale Predicted",
            message="A major festival sale is expected next week for Samsung Galaxy S24.",
            timestamp=(now - datetime.timedelta(days=1)).isoformat(),
            read=True,
            productId="seller_changed",
        )
        self._alerts[str(a1.id)] = a1
        self._alerts[str(a2.id)] = a2
        self._alerts[str(a3.id)] = a3

    def get_all(self) -> List[AlertSchema]:
        """Returns all alerts ordered with unread first."""
        with self._lock:
            return sorted(self._alerts.values(), key=lambda a: (a.read, a.id))

    def mark_as_read(self, alert_id: Union[int, str]) -> Optional[AlertSchema]:
        """Marks an alert as read."""
        key = str(alert_id)
        with self._lock:
            if key in self._alerts:
                self._alerts[key].read = True
                return self._alerts[key]
            return None


alert_service = AlertService()
