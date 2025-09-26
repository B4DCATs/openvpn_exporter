#!/bin/bash
# OpenVPN Prometheus Exporter v2.0 - Quick Start Script

set -e

# Default values
IMAGE_NAME="openvpn-exporter"
IMAGE_TAG="v2.0"
CONTAINER_NAME="openvpn-exporter"
PORT="9176"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}OpenVPN Prometheus Exporter v2.0 - Quick Start${NC}"
echo "=================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    exit 1
fi

# Build image if it doesn't exist
if ! docker image inspect "${IMAGE_NAME}:${IMAGE_TAG}" > /dev/null 2>&1; then
    echo -e "${YELLOW}Building Docker image...${NC}"
    docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" .
fi

# Stop and remove existing container if it exists
if docker ps -a --format 'table {{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${YELLOW}Stopping existing container...${NC}"
    docker stop "${CONTAINER_NAME}" > /dev/null 2>&1 || true
    docker rm "${CONTAINER_NAME}" > /dev/null 2>&1 || true
fi

# Create directories if they don't exist
mkdir -p /var/log/openvpn
mkdir -p /etc/openvpn

# Run container
echo -e "${YELLOW}Starting OpenVPN Exporter...${NC}"
docker run -d \
    --name "${CONTAINER_NAME}" \
    -p "${PORT}:9176" \
    -v /var/log/openvpn:/var/log/openvpn:ro \
    -v /etc/openvpn:/etc/openvpn:ro \
    -e STATUS_PATHS="/var/log/openvpn/server.status,/var/log/openvpn/client.status" \
    -e LOG_LEVEL="INFO" \
    -e LISTEN_ADDRESS=":9176" \
    -e TELEMETRY_PATH="/metrics" \
    -e IGNORE_INDIVIDUALS="false" \
    "${IMAGE_NAME}:${IMAGE_TAG}"

# Wait for container to start
echo -e "${YELLOW}Waiting for service to start...${NC}"
sleep 5

# Check if container is running
if docker ps --format 'table {{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${GREEN}✅ OpenVPN Exporter is running!${NC}"
    echo ""
    echo "📊 Metrics endpoint: http://localhost:${PORT}/metrics"
    echo "🏥 Health check: http://localhost:${PORT}/health"
    echo "🌐 Web interface: http://localhost:${PORT}/"
    echo ""
    echo "📝 Add this to your Prometheus config:"
    echo "  - job_name: 'openvpn-exporter'"
    echo "    static_configs:"
    echo "      - targets: ['localhost:${PORT}']"
    echo ""
    echo "🔍 View logs: docker logs ${CONTAINER_NAME}"
    echo "🛑 Stop: docker stop ${CONTAINER_NAME}"
else
    echo -e "${RED}❌ Failed to start container${NC}"
    echo "Check logs: docker logs ${CONTAINER_NAME}"
    exit 1
fi
