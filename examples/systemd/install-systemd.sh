#!/bin/bash

# OpenVPN Exporter - Systemd Service Installation Script
# This script installs OpenVPN Exporter as a systemd service

set -e

echo "🚀 OpenVPN Exporter - Systemd Service Installation"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run with root privileges"
    echo "Usage: sudo ./install-systemd.sh"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "📋 Installation steps:"
echo "  1. Create system user"
echo "  2. Install Python dependencies"
echo "  3. Copy files to /opt/openvpn-exporter"
echo "  4. Create configuration directory"
echo "  5. Install systemd service"
echo ""

# Step 1: Create system user
echo "👤 Creating system user 'openvpn-exporter'..."
if ! id "openvpn-exporter" &>/dev/null; then
    useradd -r -s /bin/false -d /opt/openvpn-exporter openvpn-exporter
    echo "✅ User created"
else
    echo "✅ User already exists"
fi

# Step 2: Install Python dependencies
echo "📦 Installing Python dependencies..."
if command -v pip3 &> /dev/null; then
    pip3 install -r "$PROJECT_DIR/requirements.txt" --quiet
    echo "✅ Dependencies installed"
else
    echo "⚠️  pip3 not found. Please install Python dependencies manually:"
    echo "   pip3 install -r $PROJECT_DIR/requirements.txt"
fi

# Step 3: Copy files to /opt/openvpn-exporter
echo "📁 Installing files to /opt/openvpn-exporter..."
mkdir -p /opt/openvpn-exporter
cp "$PROJECT_DIR/openvpn_exporter.py" /opt/openvpn-exporter/
chmod +x /opt/openvpn-exporter/openvpn_exporter.py
chown -R openvpn-exporter:openvpn-exporter /opt/openvpn-exporter
echo "✅ Files installed"

# Step 4: Create configuration directory
echo "⚙️  Creating configuration directory..."
mkdir -p /etc/openvpn-exporter
if [ ! -f /etc/openvpn-exporter/openvpn-exporter.conf ]; then
    cp "$SCRIPT_DIR/openvpn-exporter.conf" /etc/openvpn-exporter/openvpn-exporter.conf
    echo "✅ Configuration file created at /etc/openvpn-exporter/openvpn-exporter.conf"
    echo "   Please edit it with your settings before starting the service"
else
    echo "✅ Configuration file already exists"
fi

# Step 5: Install systemd service
echo "🔧 Installing systemd service..."
cp "$SCRIPT_DIR/openvpn-exporter.service" /etc/systemd/system/
systemctl daemon-reload
echo "✅ Service installed"

# Enable service (but don't start yet - user should configure first)
echo ""
echo "🎉 Installation completed!"
echo ""
echo "📝 Next steps:"
echo "  1. Edit configuration: sudo nano /etc/openvpn-exporter/openvpn-exporter.conf"
echo "  2. Set STATUS_PATHS to your OpenVPN status file path(s)"
echo "  3. (Optional) Set ALLOWED_IPS for security"
echo "  4. Start the service: sudo systemctl start openvpn-exporter"
echo "  5. Enable auto-start: sudo systemctl enable openvpn-exporter"
echo ""
echo "📊 Useful commands:"
echo "  - Check status: sudo systemctl status openvpn-exporter"
echo "  - View logs: sudo journalctl -u openvpn-exporter -f"
echo "  - Restart: sudo systemctl restart openvpn-exporter"
echo "  - Stop: sudo systemctl stop openvpn-exporter"
echo ""

