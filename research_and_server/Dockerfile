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
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# 1. Install dependencies (Cached Layer)
COPY --chown=user requirements.txt .
RUN pip install --user -r requirements.txt

# 2. Copy the 1.8GB Database (Cached Layer - Rarely changes)
# This ensures code changes don't re-upload the massive database
COPY --chown=user data/index.db data/index.db

# 3. Copy application code (Last Layer - Changes often)
COPY --chown=user . .

# Ensure necessary directories exist
RUN mkdir -p sessions data/indices

# Expose Hugging Face default port
EXPOSE 7860

# Launch the FastAPI server
CMD ["python", "-m", "uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "7860"]
