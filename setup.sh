#!/bin/bash

# OpenVPN Exporter - Automatic setup and deployment
# This script configures everything needed for the exporter to work

set -e

echo "🚀 OpenVPN Exporter - Automatic setup"

# Check if we are root or have sudo
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run with root privileges or through sudo"
    echo "Usage: sudo ./setup.sh"
    exit 1
fi

echo "📋 System check..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Install Docker and try again."
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Install Docker Compose and try again."
    exit 1
fi

echo "✅ Docker and Docker Compose found"

# Check OpenVPN
if ! systemctl is-active --quiet openvpn@server; then
    echo "⚠️  OpenVPN server is not running. Starting..."
    systemctl start openvpn@server
    sleep 2
fi

echo "✅ OpenVPN server is active"

# Create directories if they don't exist
echo "📁 Creating necessary directories..."
mkdir -p /var/log/openvpn
mkdir -p /etc/openvpn

# Setup status file permissions
echo "🔧 Setting up permissions..."

# Check if status file exists
if [ -f "/var/log/openvpn/status.log" ]; then
    echo "📄 Status file found, setting up permissions..."
    chmod 644 /var/log/openvpn/status.log
    chown root:root /var/log/openvpn/status.log
else
    echo "⚠️  Status file not found, creating empty one..."
    touch /var/log/openvpn/status.log
    chmod 644 /var/log/openvpn/status.log
    chown root:root /var/log/openvpn/status.log
fi

# Configure OpenVPN to create status file with correct permissions
echo "⚙️  Configuring OpenVPN..."

# Check OpenVPN configuration
if [ -f "/etc/openvpn/server.conf" ]; then
    # Add status settings if they don't exist
    if ! grep -q "status /var/log/openvpn/status.log" /etc/openvpn/server.conf; then
        echo "📝 Adding status settings to OpenVPN..."
        echo "" >> /etc/openvpn/server.conf
        echo "# OpenVPN Exporter settings" >> /etc/openvpn/server.conf
        echo "status /var/log/openvpn/status.log 10" >> /etc/openvpn/server.conf
        echo "status-version 2" >> /etc/openvpn/server.conf
    fi
    
    # Restart OpenVPN to apply settings
    echo "🔄 Restarting OpenVPN..."
    systemctl restart openvpn@server
    sleep 3
fi

# Check if status file was created
if [ -f "/var/log/openvpn/status.log" ]; then
    echo "✅ Status file created and configured"
    chmod 644 /var/log/openvpn/status.log
else
    echo "⚠️  Status file was not created, but continuing..."
fi

# Stop old containers if any
echo "🧹 Cleaning up old containers..."
docker-compose down 2>/dev/null || true

# Start exporter
echo "🐳 Starting OpenVPN Exporter..."
docker-compose up -d

# Wait for startup
echo "⏳ Waiting for exporter to start..."
sleep 5

# Check status
echo "🔍 Checking status..."

# Check if container started
if docker-compose ps | grep -q "Up"; then
    echo "✅ OpenVPN Exporter started successfully!"
    
    # Check metrics availability
    if curl -s http://localhost:9176/health > /dev/null 2>&1; then
        echo "✅ Metrics available at: http://localhost:9176/metrics"
        echo "✅ Health check: http://localhost:9176/health"
    else
        echo "⚠️  Exporter is running, but metrics are not yet available. Wait a few seconds."
    fi
    
    echo ""
    echo "🎉 Setup completed!"
    echo "📊 To check metrics run: curl http://localhost:9176/metrics"
    echo "🛑 To stop run: docker-compose down"
    
else
    echo "❌ Error starting exporter. Check logs:"
    echo "docker-compose logs"
    exit 1
fi
