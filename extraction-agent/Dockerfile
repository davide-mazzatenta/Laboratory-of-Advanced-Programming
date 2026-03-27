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

# Install lightweight CPU-only PyTorch and minimal dependencies
RUN pip install --upgrade pip \
    && pip install --index-url https://download.pytorch.org/whl/cpu \
        torch==2.1.1+cpu \
    && pip install  \
        fastapi==0.104.1 \
        uvicorn[standard]==0.24.0 \
        requests==2.31.0 \
        pydantic==2.5.0 \
        transformers==4.35.2 \
        tokenizers==0.15.0 \
        numpy==1.24.3 \
        python-multipart==0.0.6 \
        accelerate==0.24.1 \
        google-generativeai==0.3.2

# Pre-download model during build to avoid cold starts
RUN python -c "from transformers import AutoTokenizer, AutoModelForTokenClassification; \
    AutoTokenizer.from_pretrained('DeepMount00/Italian_NER_XXL'); \
    AutoModelForTokenClassification.from_pretrained('DeepMount00/Italian_NER_XXL', ignore_mismatched_sizes=True)" \
    && find /root/.cache -name "*.bin" -delete || true \
    && find /root/.cache -name "*.safetensors" -delete || true

# Copy source code
COPY . .

# Create non-root user for security and copy model cache
RUN useradd --create-home --shell /bin/bash app \
    && mkdir -p /home/app/.cache \
    && cp -r /root/.cache/* /home/app/.cache/ 2>/dev/null || true \
    && chown -R app:app /app /home/app/.cache
USER app

# Expose port
EXPOSE 8001

# Health check with longer timeout for model loading
HEALTHCHECK --interval=45s --timeout=45s --start-period=120s --retries=2 \
    CMD curl -f http://localhost:8001/health || exit 1

# Start service with optimized settings
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "1", "--loop", "asyncio"]