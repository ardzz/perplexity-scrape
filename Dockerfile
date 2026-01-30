# Stage 1: Builder
FROM python:3.12-slim-bookworm AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libcurl4-openssl-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim-bookworm AS runtime

LABEL org.opencontainers.image.source="https://github.com/ardzz/perplexity-mcp"
LABEL org.opencontainers.image.description="OpenAI-compatible REST API + MCP Server for Perplexity AI"
LABEL org.opencontainers.image.licenses="MIT"

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcurl4 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser combined_server.py .
COPY --chown=appuser:appuser rest_server.py .
COPY --chown=appuser:appuser server.py .
COPY --chown=appuser:appuser perplexity_client.py .
COPY --chown=appuser:appuser src/ ./src/

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8045

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8045/ || exit 1

# Run the combined server (REST API + MCP on same port)
CMD ["python", "-m", "uvicorn", "combined_server:app", "--host", "0.0.0.0", "--port", "8045"]
