# EzDB Docker Image
# Unified RDBMS + Vector Database with Web Interface

FROM python:3.10-slim

# Set metadata
LABEL maintainer="EzDB Project"
LABEL description="Unified RDBMS and Vector Database with AI-powered semantic search"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

# Default configuration (can be overridden)
ENV EZDB_PORT=8000 \
    EZDB_HOST=0.0.0.0 \
    EZDB_SERVICE_NAME=ezdb \
    EZDB_DATA_DIR=/data

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    g++ \
    gcc \
    make \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Create data directory
RUN mkdir -p /data && chmod 777 /data

# Install Python dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    numpy \
    hnswlib \
    sentence-transformers \
    torch \
    scipy \
    requests \
    starlette \
    python-multipart

# Copy application code
COPY ezdb/ /app/ezdb/
COPY LICENSE /app/
COPY README.md /app/

# Copy startup script
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Expose default port (can be changed via ENV)
EXPOSE ${EZDB_PORT}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${EZDB_PORT}/health || exit 1

# Set volume for persistent data
VOLUME ["/data"]

# Set working directory
WORKDIR /app

# Use entrypoint script
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Default command (can be overridden)
CMD ["server"]
