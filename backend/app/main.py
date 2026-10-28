from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import logger
from app.api.routes import (
    health_router,
    search_router,
    analyze_router,
    products_router,
    watchlist_router,
    alerts_router,
    preferences_router,
    notifications_router,
    auth_router,
)

try:
    from app.core.middleware import setup_security_middlewares
    HAS_SECURITY_MIDDLEWARE = True
except ImportError:
    HAS_SECURITY_MIDDLEWARE = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle event handler for application startup and teardown."""
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} [{settings.ENVIRONMENT}]")
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME}")


def create_application() -> FastAPI:
    """FastAPI Application Factory."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="ShopQ Intelligent Commerce Decision Engine API",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Attach security middlewares (CORS, Request ID, Security Headers, Rate Limiting)
    if HAS_SECURITY_MIDDLEWARE:
        setup_security_middlewares(app, settings.CORS_ORIGINS)
    else:
        # Allow all origins for demo & development; tighten in production via ALLOWED_ORIGINS env var
        cors_origins = settings.CORS_ORIGINS if settings.IS_PRODUCTION else ["*"]
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=False if cors_origins == ["*"] else True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Health endpoints (available at /health and /api/health)
    app.include_router(health_router)
    app.include_router(health_router, prefix=settings.API_PREFIX)

    # Core API endpoints under /api
    app.include_router(search_router, prefix=settings.API_PREFIX)
    app.include_router(analyze_router, prefix=settings.API_PREFIX)
    app.include_router(products_router, prefix=settings.API_PREFIX)
    app.include_router(watchlist_router, prefix=settings.API_PREFIX)
    app.include_router(alerts_router, prefix=settings.API_PREFIX)
    app.include_router(preferences_router, prefix=settings.API_PREFIX)
    app.include_router(notifications_router, prefix=settings.API_PREFIX)
    app.include_router(auth_router, prefix=settings.API_PREFIX)

    @app.get("/", include_in_schema=False)
    def root():
        return JSONResponse(
            content={
                "service": settings.PROJECT_NAME,
                "version": settings.VERSION,
                "docs": "/docs",
                "health": "/health",
                "endpoints": {
                    "health": "GET /health",
                    "search": "POST /api/search",
                    "analyze": "POST /api/analyze",
                    "product": "GET /api/products/{id}",
                    "analysis": "GET /api/products/{id}/analysis",
                    "details": "GET /api/products/{id}/details",
                    "offers": "GET /api/products/{id}/offers",
                    "price_history": "GET /api/products/{id}/price-history",
                    "watchlist": "GET/POST /api/watchlist, DELETE /api/watchlist/{id}",
                    "alerts": "GET /api/alerts, POST /api/alerts/{id}/read",
                    "preferences": "GET/PUT /api/preferences",
                },
            }
        )

    return app


app = create_application()
