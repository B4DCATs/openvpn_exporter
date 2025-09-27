#!/bin/bash

# OpenVPN Prometheus Exporter Quick Start Script
# This script downloads and runs the OpenVPN exporter without cloning the repository

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
COMPOSE_URL="https://raw.githubusercontent.com/B4DCATs/openvpn_exporter/main/docker-compose.yml"
WORK_DIR="/opt/openvpn-exporter"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first:"
        echo "  Ubuntu/Debian: apt-get update && apt-get install docker.io"
        echo "  CentOS/RHEL: yum install docker"
        echo "  Or visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first:"
        echo "  Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi
}

check_openvpn_status() {
    local status_paths=("/var/log/openvpn/server.status" "/etc/openvpn/server.status" "/var/log/openvpn/openvpn-status.log")
    local found=false
    
    for path in "${status_paths[@]}"; do
        if [[ -f "$path" ]]; then
            log_success "Found OpenVPN status file: $path"
            found=true
            break
        fi
    done
    
    if [[ "$found" == false ]]; then
        log_warning "No OpenVPN status file found in common locations."
        log_warning "Make sure OpenVPN server is configured with status logging."
        log_warning "Common locations: /var/log/openvpn/server.status, /etc/openvpn/server.status"
        echo
        read -p "Do you want to continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

download_compose_file() {
    log_info "Downloading docker-compose.yml..."
    
    # Create work directory
    mkdir -p "$WORK_DIR"
    cd "$WORK_DIR"
    
    # Download compose file
    if curl -fsSL "$COMPOSE_URL" -o "$COMPOSE_FILE"; then
        log_success "Downloaded docker-compose.yml"
    else
        log_error "Failed to download docker-compose.yml"
        exit 1
    fi
}

setup_permissions() {
    log_info "Setting up permissions..."
    
    # Ensure Docker daemon is running
    systemctl start docker 2>/dev/null || true
    
    # Create necessary directories with proper permissions
    mkdir -p /var/log/openvpn /etc/openvpn
    chmod 755 /var/log/openvpn /etc/openvpn
    
    log_success "Permissions configured"
}

start_exporter() {
    log_info "Starting OpenVPN Prometheus Exporter..."
    
    # Use docker-compose or docker compose
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi
    
    # Start the exporter
    if $COMPOSE_CMD up -d; then
        log_success "OpenVPN Prometheus Exporter started successfully!"
    else
        log_error "Failed to start OpenVPN Prometheus Exporter"
        exit 1
    fi
}

show_status() {
    log_info "Checking exporter status..."
    
    # Wait a moment for container to start
    sleep 3
    
    # Check if container is running
    if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "openvpn-exporter"; then
        log_success "Container is running!"
        echo
        echo "📊 Metrics endpoint: http://$(hostname -I | awk '{print $1}'):9176/metrics"
        echo "🏥 Health check: http://$(hostname -I | awk '{print $1}'):9176/health"
        echo
        echo "📋 Useful commands:"
        echo "  View logs: docker logs openvpn-exporter"
        echo "  Stop: cd $WORK_DIR && docker-compose down"
        echo "  Restart: cd $WORK_DIR && docker-compose restart"
        echo
        log_info "To import the Grafana dashboard, download dashboard.json from:"
        echo "  https://raw.githubusercontent.com/B4DCATs/openvpn_exporter/main/dashboard.json"
    else
        log_error "Container failed to start. Check logs with: docker logs openvpn-exporter"
        exit 1
    fi
}

main() {
    echo "🚀 OpenVPN Prometheus Exporter Quick Start"
    echo "=========================================="
    echo
    
    check_root
    check_docker
    check_openvpn_status
    download_compose_file
    setup_permissions
    start_exporter
    show_status
    
    echo
    log_success "Setup complete! 🎉"
}

# Run main function
main "$@"
