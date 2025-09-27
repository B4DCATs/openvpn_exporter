# OpenVPN Status File Examples

This directory contains example OpenVPN status files in different formats that are supported by the OpenVPN Prometheus Exporter.

## 📋 Supported Formats

### 1. Client Statistics Format (`client.status`)
Standard OpenVPN client statistics format with comma-separated values.

**Features:**
- Client connection information
- Traffic statistics (bytes received/sent)
- Connection timestamps
- Routing table information

### 2. Server Statistics v2 (`server2.status`)
OpenVPN server statistics version 2 with comma-delimited format.

**Features:**
- All client statistics features
- Connection time as Unix timestamp
- Enhanced client tracking

### 3. Server Statistics v3 (`server3.status`)
OpenVPN server statistics version 3 with tab-delimited format.

**Features:**
- All server v2 features
- Tab-separated values instead of commas
- Most modern format

## 🔧 Configuration

To use these examples with the OpenVPN Exporter:

```bash
# Test with example files
python openvpn_exporter.py --openvpn.status_paths=examples/status/client.status,examples/status/server2.status,examples/status/server3.status
```

```yaml
# Docker Compose example
environment:
  - STATUS_PATHS=examples/status/client.status,examples/status/server2.status,examples/status/server3.status
```

## 📊 Generated Metrics

The exporter will generate the following metrics from these status files:

- `openvpn_server_client_count` - Number of connected clients
- `openvpn_server_client_received_bytes_total` - Total bytes received per client
- `openvpn_server_client_sent_bytes_total` - Total bytes sent per client
- `openvpn_server_client_connection_time` - Client connection timestamp
- `openvpn_up` - Server availability status

## 🚀 Testing

You can test the exporter with these example files:

```bash
# Start the exporter with example status files
python openvpn_exporter.py --openvpn.status_paths=examples/status/client.status

# Check metrics
curl http://localhost:9176/metrics
```

## 📝 Notes

- These are example files with sample data
- Replace with your actual OpenVPN status file paths
- Ensure the OpenVPN server is configured to write status files
- Status files should be readable by the exporter process

## 🔗 OpenVPN Configuration

To enable status file generation in OpenVPN, add to your server configuration:

```
# Status file (updated every 30 seconds)
status /var/log/openvpn/server.status 30

# Or for client statistics
status-version 2
status /var/log/openvpn/client.status 30
```
