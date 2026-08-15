# ── Stage 1: Build Frontend ──────────────────────────────────────────────────
FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY dashboard-web/package*.json ./
RUN npm ci --prefer-offline --no-audit
COPY dashboard-web/ ./
RUN npm run build

# ── Stage 2: Python dependencies builder ─────────────────────────────────────
FROM python:3.11-slim AS python-builder
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ── Stage 3: Runtime image ───────────────────────────────────────────────────
FROM python:3.11-slim
LABEL maintainer="Career-Ops" version="3.5.0"

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY --from=python-builder /root/.local /root/.local
COPY --from=frontend-builder /app/dist ./dashboard-web/dist

COPY career_ops_api.py direct_scoring.py adzuna_provider.py jsearch_provider.py ./
COPY config/ ./config/

RUN mkdir -p reports output resumes latex_resumes

ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/stats || exit 1

EXPOSE 5000

CMD ["python", "career_ops_api.py"]
