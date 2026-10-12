#!/usr/bin/env python3
"""ShopQ Backend Server Runner."""

import os
import sys

# Ensure current backend root is on Python module search path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import uvicorn
from app.core.config import settings

def main():
    host = os.getenv("HOST", settings.SERVER_HOST)
    port = int(os.getenv("PORT", settings.SERVER_PORT))
    reload = os.getenv("RELOAD", "true").lower() == "true"

    print("=" * 60)
    print(f"  Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"  Listening on http://{host}:{port}")
    print(f"  API Docs available at http://{host}:{port}/docs")
    print(f"  Health Check at http://{host}:{port}/health")
    print("=" * 60)

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )

if __name__ == "__main__":
    main()
