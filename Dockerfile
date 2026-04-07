# ── Build target: linux/amd64 (HuggingFace Spaces requirement) ───────────────
FROM --platform=linux/amd64 python:3.11-slim

# Metadata
LABEL maintainer="Antigravity"
LABEL description="PR Review & Security Audit OpenEnv Environment"

# Set working directory
WORKDIR /app

# Install dependencies first (cached layer if requirements.txt unchanged)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY app/ ./app/
COPY data/ ./data/
COPY openenv.yaml .

# HuggingFace Spaces runs containers as a non-root user (UID 1000)
# Create that user here so file permissions work correctly
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Port 7860 is required by HuggingFace Spaces — do not change
EXPOSE 7860

# Start the FastAPI server
# --workers 1 keeps the Environment singleton consistent across requests
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]