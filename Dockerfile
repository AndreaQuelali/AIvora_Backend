# Multi-stage Dockerfile for AIvora Backend
# Stage 1 (builder): installs Python deps into a venv
# Stage 2 (runtime): minimal image with only the venv and app code

# ============================================================
# Stage 1 — Builder
# ============================================================
FROM python:3.13-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtualenv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies (layer cached independently)
COPY pyproject.toml .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -e .


# ============================================================
# Stage 2 — Runtime
# ============================================================
FROM python:3.13-slim AS runtime

WORKDIR /app

# Runtime system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Non-root user for security
RUN groupadd --gid 1001 aivora && \
    useradd --uid 1001 --gid aivora --shell /bin/bash --create-home aivora

# Copy virtualenv from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --chown=aivora:aivora . .

# Create upload dir
RUN mkdir -p /app/uploads && chown -R aivora:aivora /app/uploads

USER aivora

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health/live || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
