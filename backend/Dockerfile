# ==============================================================================
# ShopQ Backend - Production Multi-Stage Dockerfile
# Base: python:3.11-slim
# Server: Uvicorn ASGI server
# Security: Non-root user execution, multi-stage build, minimal attack surface
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Builder
# ------------------------------------------------------------------------------
FROM python:3.11-slim AS builder

# Prevent Python from writing bytecode and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Install build dependencies required for compiling native extensions
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl && \
    rm -rf /var/lib/apt/lists/*

# Create virtual environment for isolated dependency packaging
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python requirements
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# ------------------------------------------------------------------------------
# Stage 2: Production Runner
# ------------------------------------------------------------------------------
FROM python:3.11-slim AS runner

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    HOST=0.0.0.0 \
    PORT=8000 \
    ENVIRONMENT=production

# Install curl for reliable container healthchecks
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Create non-root system group and user
RUN groupadd --system --gid 10001 shopq && \
    useradd --system --uid 10001 --gid shopq --create-home --home-dir /home/shopq --shell /bin/false shopq

WORKDIR /app

# Copy isolated virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application codebase with non-root ownership
COPY --chown=shopq:shopq app /app/app
COPY --chown=shopq:shopq database /app/database
COPY --chown=shopq:shopq run.py /app/run.py
COPY --chown=shopq:shopq requirements.txt /app/requirements.txt

# Switch to non-root execution
USER shopq

# Expose default port
EXPOSE 8000

# Container healthcheck against /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f "http://localhost:${PORT:-8000}/health" || exit 1

# Execute Uvicorn server, supporting dynamic $PORT from cloud runtime platforms (Render, Fly.io, Cloud Run)
CMD ["sh", "-c", "exec uvicorn app.main:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000} --workers ${WORKERS:-2} --proxy-headers --forwarded-allow-ips='*'"]
