# Use Python base image
FROM python:3.11-slim

# Set environment variables for better Python performance and lighter builds
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    # Cleanup to reduce image size
    && rm -rf /var/lib/apt/lists/* \
    && apt-get autoremove -y \
    && apt-get clean

# Install lightweight dependencies (no heavy ML models needed)
RUN pip install --upgrade pip \
    && pip install \
        fastapi==0.104.1 \
        uvicorn[standard]==0.24.0 \
        requests==2.31.0 \
        pydantic==2.5.0 \
        python-multipart==0.0.6 \
        google-generativeai==0.3.2

# Copy source code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8003

# Health check with standard timeout
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8003/health || exit 1

# Start service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003", "--workers", "1", "--loop", "asyncio"]