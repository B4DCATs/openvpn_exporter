#!/bin/bash

# OpenVPN Exporter - Simple startup
# Automatically configures and starts the exporter

set -e

echo "🚀 OpenVPN Exporter - Simple startup"

# Check permissions
if [ "$EUID" -ne 0 ]; then
    echo "❌ Run with root privileges: sudo ./run.sh"
    exit 1
fi

# Quick setup of status file permissions
echo "🔧 Setting up permissions..."
if [ -f "/var/log/openvpn/status.log" ]; then
    chmod 644 /var/log/openvpn/status.log 2>/dev/null || true
fi

# Start exporter
echo "🐳 Starting OpenVPN Exporter..."
docker-compose up -d

echo "✅ Done! Exporter is running at http://localhost:9176"
echo "📊 Metrics: http://localhost:9176/metrics"
echo "🛑 Stop: docker-compose down"