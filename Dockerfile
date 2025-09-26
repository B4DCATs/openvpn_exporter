# OpenVPN Prometheus Exporter v2.0 - Python Implementation
# Multi-stage build for security and size optimization

# Build stage
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# No system dependencies needed - all Python packages are pure Python

# Create and set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.local/bin:$PATH"

# Create non-root user for security
RUN groupadd -r openvpn-exporter && \
    useradd -r -g openvpn-exporter -d /app -s /bin/false openvpn-exporter

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application files
COPY openvpn_exporter.py .
COPY examples/ examples/

# Create directories for OpenVPN status files
RUN mkdir -p /var/log/openvpn /etc/openvpn /tmp/openvpn && \
    chown -R openvpn-exporter:openvpn-exporter /app /var/log/openvpn /etc/openvpn /tmp/openvpn

# Switch to non-root user
USER openvpn-exporter

# Expose port
EXPOSE 9176

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:9176/health')" || exit 1

# Run the application
ENTRYPOINT ["python", "openvpn_exporter.py"]
CMD []