# ──────────────────────────────────────────────────────────
# ML Observability Platform — Dockerfile
# Multi-stage build for the FastAPI application
# ──────────────────────────────────────────────────────────

# ── Stage 1: Builder ─────────────────────────────────────

FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: Production ─────────────────────────────────

FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY config.py .
COPY app/ ./app/
COPY monitoring/ ./monitoring/
COPY training/ ./training/
COPY saved_models/ ./saved_models/
COPY data/ ./data/

# Expose FastAPI port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
