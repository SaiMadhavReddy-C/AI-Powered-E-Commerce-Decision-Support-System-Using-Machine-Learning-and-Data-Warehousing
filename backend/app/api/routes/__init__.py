"""Route modules for ShopQ backend."""

from app.api.routes.health import router as health_router
from app.api.routes.search import router as search_router
from app.api.routes.analyze import router as analyze_router
from app.api.routes.products import router as products_router
from app.api.routes.watchlist import router as watchlist_router
from app.api.routes.alerts import router as alerts_router
from app.api.routes.preferences import router as preferences_router
from app.api.routes.notifications import router as notifications_router
from app.api.routes.auth import router as auth_router

__all__ = [
    "health_router",
    "search_router",
    "analyze_router",
    "products_router",
    "watchlist_router",
    "alerts_router",
    "preferences_router",
    "notifications_router",
    "auth_router",
]
