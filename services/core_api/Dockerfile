# Production-Grade Dockerfile for Legal AI Backend
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and switch to non-root user
RUN useradd -m -u 1000 user
WORKDIR /app

# Ensure directories exist and are owned by user
RUN mkdir -p /app/sessions /app/data/indices && chown -R user:user /app

USER user
ENV PATH="/home/user/.local/bin:$PATH"

# 1. Install dependencies (Cached Layer)
COPY --chown=user requirements.txt .
RUN pip install --user -r requirements.txt

# 2. Copy application code (Last Layer - Changes often)
COPY --chown=user . .

# Expose port (Cloud Run will inject PORT, default to 8080)
EXPOSE 8080

# Launch the FastAPI server
CMD exec uvicorn hybrid_search.api:app --host 0.0.0.0 --port ${PORT:-8080}
