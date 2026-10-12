"""Security Middleware and Exception Handlers for FastAPI / Starlette applications.

Includes:
- RequestIDMiddleware: Injects and traces unique X-Request-ID for every request.
- SecurityHeadersMiddleware: Sets OWASP-recommended security headers on all responses.
- AnalyzeRateLimiterMiddleware: Enforces sliding-window rate limits on /api/analyze.
- register_security_exception_handlers: Converts all application exceptions to the
  ShopQ standard error contract: {"error": {"code": "...", "message": "...", "request_id": "..."}}.
"""

from __future__ import annotations

import logging
import uuid
from typing import Callable, Optional

from app.core.security import (
    DisallowedDomainError,
    InvalidURLError,
    RateLimitExceededError,
    SSRFProtectionError,
    SecurityError,
    analyze_rate_limiter,
    format_error_response,
    get_current_request_id,
    get_security_headers,
    mask_secrets,
    request_id_ctx,
)

logger = logging.getLogger("shopq.security")

# Try to import FastAPI / Starlette components
try:
    from fastapi import FastAPI, HTTPException, Request, Response
    from fastapi.exceptions import RequestValidationError
    from fastapi.responses import JSONResponse
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.types import ASGIApp
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    # Mock classes for standalone type-hinting if FastAPI is not installed in the current environment
    class Request:  # type: ignore
        pass

    class Response:  # type: ignore
        pass

    class JSONResponse:  # type: ignore
        def __init__(self, content: dict, status_code: int = 200, headers: Optional[dict] = None):
            self.content = content
            self.status_code = status_code
            self.headers = headers or {}

    class BaseHTTPMiddleware:  # type: ignore
        def __init__(self, app: any):
            self.app = app

    class HTTPException(Exception):  # type: ignore
        def __init__(self, status_code: int, detail: str = ""):
            self.status_code = status_code
            self.detail = detail

    class RequestValidationError(Exception):  # type: ignore
        def __init__(self, errors: list):
            self.errors = errors


def get_client_ip(request: Request) -> str:
    """Safely extract client IP from request, honoring X-Forwarded-For if available."""
    try:
        x_forwarded_for = request.headers.get("x-forwarded-for")
        if x_forwarded_for:
            # First IP in the list is the original client
            client_ip = x_forwarded_for.split(",")[0].strip()
            if client_ip:
                return client_ip
        if hasattr(request, "client") and request.client and request.client.host:
            return request.client.host
    except Exception:
        pass
    return "127.0.0.1"


if HAS_FASTAPI:

    class RequestIDMiddleware(BaseHTTPMiddleware):
        """Assigns or propagates X-Request-ID for every request and injects it into context."""

        async def dispatch(self, request: Request, call_next: Callable) -> Response:
            # Read incoming X-Request-ID or generate new UUIDv4
            req_id = request.headers.get("x-request-id")
            if not req_id or len(req_id) > 64:
                req_id = str(uuid.uuid4())

            # Store in context variable and request state
            token = request_id_ctx.set(req_id)
            request.state.request_id = req_id

            try:
                response = await call_next(request)
                response.headers["X-Request-ID"] = req_id
                return response
            finally:
                request_id_ctx.reset(token)

    class SecurityHeadersMiddleware(BaseHTTPMiddleware):
        """Injects OWASP security response headers into all HTTP responses."""

        async def dispatch(self, request: Request, call_next: Callable) -> Response:
            response = await call_next(request)
            headers_to_add = get_security_headers()
            for header_name, header_value in headers_to_add.items():
                response.headers[header_name] = header_value
            return response

    class AnalyzeRateLimiterMiddleware(BaseHTTPMiddleware):
        """Intercepts calls to /api/analyze and enforces the rate limiter."""

        def __init__(self, app: ASGIApp, target_path: str = "/api/analyze"):
            super().__init__(app)
            self.target_path = target_path

        async def dispatch(self, request: Request, call_next: Callable) -> Response:
            # Bypass CORS preflight requests
            if request.method.upper() == "OPTIONS":
                return await call_next(request)

            if request.url.path.rstrip("/") == self.target_path.rstrip("/"):
                client_ip = get_client_ip(request)
                allowed, remaining, retry_after = analyze_rate_limiter.record(client_ip)

                if not allowed:
                    req_id = getattr(request.state, "request_id", get_current_request_id())
                    logger.warning(
                        "Rate limit exceeded for IP %s on %s. Retry after: %ss. Request ID: %s",
                        mask_secrets(client_ip),
                        self.target_path,
                        retry_after,
                        req_id,
                    )
                    error_payload = format_error_response(
                        code="RATE_LIMIT_EXCEEDED",
                        message=f"Rate limit exceeded. Please wait {int(retry_after)} seconds before analyzing another product.",
                        request_id=req_id,
                    )
                    return JSONResponse(
                        status_code=429,
                        content=error_payload,
                        headers={
                            "Retry-After": str(int(retry_after)),
                            "X-Request-ID": req_id,
                        },
                    )

            return await call_next(request)

    async def check_analyze_rate_limit(request: Request) -> None:
        """FastAPI route dependency alternative for rate limiting /api/analyze."""
        client_ip = get_client_ip(request)
        allowed, remaining, retry_after = analyze_rate_limiter.record(client_ip)
        if not allowed:
            raise RateLimitExceededError(
                message=f"Rate limit exceeded. Please wait {int(retry_after)} seconds.",
                retry_after=retry_after,
            )

    def register_security_exception_handlers(app: FastAPI) -> None:
        """Register centralized exception handlers complying with ShopQ standard error response contract."""

        @app.exception_handler(SSRFProtectionError)
        async def ssrf_exception_handler(request: Request, exc: SSRFProtectionError) -> JSONResponse:
            req_id = getattr(request.state, "request_id", get_current_request_id())
            logger.warning("SSRF violation caught: %s [Request: %s]", exc.message, req_id)
            return JSONResponse(
                status_code=400,
                content=format_error_response(code="SSRF_DETECTED", message=exc.message, request_id=req_id),
                headers={"X-Request-ID": req_id},
            )

        @app.exception_handler(DisallowedDomainError)
        async def disallowed_domain_handler(request: Request, exc: DisallowedDomainError) -> JSONResponse:
            req_id = getattr(request.state, "request_id", get_current_request_id())
            return JSONResponse(
                status_code=400,
                content=format_error_response(code="DISALLOWED_DOMAIN", message=exc.message, request_id=req_id),
                headers={"X-Request-ID": req_id},
            )

        @app.exception_handler(InvalidURLError)
        async def invalid_url_handler(request: Request, exc: InvalidURLError) -> JSONResponse:
            req_id = getattr(request.state, "request_id", get_current_request_id())
            return JSONResponse(
                status_code=400,
                content=format_error_response(code="INVALID_URL", message=exc.message, request_id=req_id),
                headers={"X-Request-ID": req_id},
            )

        @app.exception_handler(RateLimitExceededError)
        async def rate_limit_handler(request: Request, exc: RateLimitExceededError) -> JSONResponse:
            req_id = getattr(request.state, "request_id", get_current_request_id())
            return JSONResponse(
                status_code=429,
                content=format_error_response(code="RATE_LIMIT_EXCEEDED", message=exc.message, request_id=req_id),
                headers={
                    "Retry-After": str(int(exc.retry_after)),
                    "X-Request-ID": req_id,
                },
            )

        @app.exception_handler(SecurityError)
        async def generic_security_handler(request: Request, exc: SecurityError) -> JSONResponse:
            req_id = getattr(request.state, "request_id", get_current_request_id())
            return JSONResponse(
                status_code=400,
                content=format_error_response(code=exc.code, message=exc.message, request_id=req_id),
                headers={"X-Request-ID": req_id},
            )

        @app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
            req_id = getattr(request.state, "request_id", get_current_request_id())
            code_map = {
                400: "BAD_REQUEST",
                401: "UNAUTHORIZED",
                403: "FORBIDDEN",
                404: "NOT_FOUND",
                422: "VALIDATION_ERROR",
                429: "RATE_LIMIT_EXCEEDED",
                500: "INTERNAL_SERVER_ERROR",
            }
            code = code_map.get(exc.status_code, "HTTP_ERROR")
            return JSONResponse(
                status_code=exc.status_code,
                content=format_error_response(code=code, message=str(exc.detail), request_id=req_id),
                headers={"X-Request-ID": req_id},
            )

        @app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
            req_id = getattr(request.state, "request_id", get_current_request_id())
            # Provide clean, human-readable summary without leaking internal code logic
            error_msg = "Invalid input payload parameters."
            if exc.errors():
                first_err = exc.errors()[0]
                loc = " -> ".join(str(l) for l in first_err.get("loc", []))
                msg = first_err.get("msg", "Invalid value")
                error_msg = f"Validation failed at '{loc}': {msg}"

            return JSONResponse(
                status_code=422,
                content=format_error_response(code="VALIDATION_ERROR", message=error_msg, request_id=req_id),
                headers={"X-Request-ID": req_id},
            )

        @app.exception_handler(Exception)
        async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
            req_id = getattr(request.state, "request_id", get_current_request_id())
            # Log exception securely with secret masking
            logger.error(
                "Unhandled system error [Request ID: %s]: %s",
                req_id,
                mask_secrets(str(exc)),
                exc_info=True,
            )
            # NEVER expose stack trace, database query, or system paths to client
            return JSONResponse(
                status_code=500,
                content=format_error_response(
                    code="INTERNAL_SERVER_ERROR",
                    message="An internal server error occurred. Please try again later.",
                    request_id=req_id,
                ),
                headers={"X-Request-ID": req_id},
            )

    def setup_security_middlewares(app: FastAPI, allowed_origins: Optional[list] = None) -> None:
        """Convenience utility to attach all ShopQ security middlewares and exception handlers."""
        from fastapi.middleware.cors import CORSMiddleware
        from app.core.security import get_cors_config

        # 1. CORS Middleware
        cors_kwargs = get_cors_config(allowed_origins)
        app.add_middleware(CORSMiddleware, **cors_kwargs)

        # 2. Rate limiter for /api/analyze
        app.add_middleware(AnalyzeRateLimiterMiddleware, target_path="/api/analyze")

        # 3. Security response headers
        app.add_middleware(SecurityHeadersMiddleware)

        # 4. Request ID tracing
        app.add_middleware(RequestIDMiddleware)

        # 5. Global standardized error handlers
        register_security_exception_handlers(app)

else:
    # Fallback stubs if FastAPI is not installed
    def register_security_exception_handlers(app: any) -> None:
        pass

    async def check_analyze_rate_limit(request: any) -> None:
        pass

    def setup_security_middlewares(app: any, allowed_origins: Optional[list] = None) -> None:
        pass

