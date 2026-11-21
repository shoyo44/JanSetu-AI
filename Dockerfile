# ── Stage 1: Build & Dependencies ──────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Build dependencies for PyMuPDF and C extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Pre-download spaCy NER model into user directory
RUN python -m pip install --no-cache-dir --user \
    https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.0/en_core_web_sm-3.7.0-py3-none-any.whl


# ── Stage 2: Hardened Non-Root Runtime ────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Install minimal runtime libraries & Indic OCR language packs
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    tesseract-ocr \
    tesseract-ocr-hin \
    tesseract-ocr-tam \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Security: Create isolated non-root user and group (UID/GID 10001)
RUN groupadd -g 10001 docqa && \
    useradd -u 10001 -g docqa -s /bin/bash -m docqa

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /root/.local /home/docqa/.local

# Set environment variables
ENV PATH=/home/docqa/.local/bin:$PATH \
    PYTHONPATH=/app/backend \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    GRAPH_STORE_DIR=/app/backend/data

# Copy backend application source
COPY --chown=docqa:docqa backend/ /app/backend/
COPY --chown=docqa:docqa eval/ /app/eval/

# Ensure state directories exist with correct non-root permissions
RUN mkdir -p /app/backend/data /app/backend/temp && \
    chown -R docqa:docqa /app

# Drop root privileges
USER docqa

EXPOSE 8000

# Container Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

WORKDIR /app/backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
