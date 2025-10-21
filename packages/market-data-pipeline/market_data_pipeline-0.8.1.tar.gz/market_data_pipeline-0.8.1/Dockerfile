# ---------- Build stage ----------
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build deps (removed later)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirement files first (for Docker cache)
COPY pyproject.toml requirements.txt ./

# Install dependencies into /install
RUN pip install --upgrade pip wheel setuptools \
    && pip install --prefix=/install --no-cache-dir -r requirements.txt

# ---------- Runtime stage ----------
FROM python:3.11-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy source code
COPY src/ ./src/

# Add runtime env defaults
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    UVICORN_WORKERS=1

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

# Expose port for API
EXPOSE 8083

# Healthcheck (FastAPI /health endpoint)
HEALTHCHECK CMD curl --fail http://localhost:8083/health || exit 1

# Default command
CMD ["uvicorn", "market_data_pipeline.runners.api:app", "--host", "0.0.0.0", "--port", "8083"]
