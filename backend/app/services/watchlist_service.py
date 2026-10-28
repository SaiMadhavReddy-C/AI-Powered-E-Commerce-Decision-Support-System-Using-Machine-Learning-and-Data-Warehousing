import threading
from typing import List, Optional, Dict
from app.schemas.watchlist import WatchlistItemSchema, WatchlistStatusSchema
from app.services.product_service import product_service
from app.core.config import settings

class WatchlistService:
    """Manages the user watchlist with dynamic status evaluations."""

    def __init__(self):
        self._lock = threading.Lock()
        self._items: Dict[str, WatchlistItemSchema] = {}
        self._init_seed_items()

    def _init_seed_items(self):
        if settings.IS_PRODUCTION:
            return
        # 1. iPhone 15
        p_iphone = product_service.get_by_id("iphone_wait")
        if p_iphone:
            self._items[p_iphone.id] = WatchlistItemSchema(
                **p_iphone.model_dump(by_alias=True),
                targetPrice=54999.0,
                watchGroup="BUY_SIGNAL",
                watchMessage="🔥 Price dropped to ₹54,999. I'd buy it now.",
                watchStatus=WatchlistStatusSchema(
                    emoji="🔥",
                    icon="🔥",
                    message="Price dropped to ₹54,999. I'd buy it now.",
                    type="positive",
                ),
                actionLabel="Buy now",
                lastCheckedText="Last checked 2 min ago",
            )

        # 2. Sony WH-1000XM5
        p_sony = product_service.get_by_id("sony_good_deal")
        if p_sony:
            self._items[p_sony.id] = WatchlistItemSchema(
                **p_sony.model_dump(by_alias=True),
                targetPrice=22999.0,
                watchGroup="WAITING",
                watchMessage="⏳ Still waiting. I'd reconsider around ₹22,999.",
                watchStatus=WatchlistStatusSchema(
                    emoji="⏳",
                    icon="⏳",
                    message="Still waiting. I'd reconsider around ₹22,999.",
                    type="warning",
                ),
                actionLabel="Check now",
                lastCheckedText="Last checked 4 min ago",
            )

        # 3. Samsung Galaxy S24
        p_samsung = product_service.get_by_id("seller_changed")
        if p_samsung:
            self._items[p_samsung.id] = WatchlistItemSchema(
                **p_samsung.model_dump(by_alias=True),
                targetPrice=54999.0,
                watchGroup="NEEDS_ATTENTION",
                watchMessage="⚠️ The seller changed. I'd check the new listing before buying.",
                watchStatus=WatchlistStatusSchema(
                    emoji="⚠️",
                    icon="⚠️",
                    message="The seller changed. I'd check the new listing before buying.",
                    type="danger",
                ),
                actionLabel="Review",
                lastCheckedText="Last checked 1 hr ago",
            )

        # 4. Canon EOS R50
        p_camera = product_service.get_by_id("new_product_no_history")
        if p_camera:
            self._items[p_camera.id] = WatchlistItemSchema(
                **p_camera.model_dump(by_alias=True),
                targetPrice=69999.0,
                watchGroup="WATCHING",
                watchMessage="👀 Monitoring prices. No major drops yet.",
                watchStatus=WatchlistStatusSchema(
                    emoji="👀",
                    icon="👀",
                    message="Monitoring prices. No major drops yet.",
                    type="neutral",
                ),
                actionLabel="Check now",
                lastCheckedText="Last checked 3 hrs ago",
            )

    def get_all(self) -> List[WatchlistItemSchema]:
        """Returns all watchlist entries."""
        with self._lock:
            return list(self._items.values())

    def add(self, product_id: str, target_price: Optional[float] = None) -> Optional[WatchlistItemSchema]:
        """Adds a product to the watchlist or updates its target price."""
        product = product_service.get_by_id(product_id)
        if not product:
            product = product_service.resolve_by_url(product_id)
        if not product:
            return None

        effective_target = target_price if target_price is not None else product.buy_point or (product.current_price * 0.9)

        with self._lock:
            item = WatchlistItemSchema(
                **product.model_dump(by_alias=True),
                targetPrice=effective_target,
                watchGroup="WATCHING",
                watchMessage=f"👀 Monitoring {product.name}. Target set to ₹{effective_target:,.0f}.",
                watchStatus=WatchlistStatusSchema(
                    emoji="👀",
                    icon="👀",
                    message="Monitoring price fluctuations",
                    type="neutral",
                ),
                actionLabel="Check now",
                lastCheckedText="Just added",
            )
            self._items[product.id] = item
            return item

    def delete(self, product_id: str) -> bool:
        """Removes a product from the watchlist."""
        with self._lock:
            if product_id in self._items:
                del self._items[product_id]
                return True
            # Also check alias
            p = product_service.get_by_id(product_id)
            if p and p.id in self._items:
                del self._items[p.id]
                return True
            return False


watchlist_service = WatchlistService()
