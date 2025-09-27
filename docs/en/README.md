# OpenVPN Prometheus Exporter v2.0

**Enhanced Python implementation with improved security features**

This repository provides a secure Prometheus metrics exporter for [OpenVPN](https://openvpn.net/). The v2.0 release is a complete rewrite in Python with significant security improvements and enhanced functionality.

## 📚 Documentation

[🇺🇸](README.md) (current) [🇷🇺](../ru/README.md)

## 🚀 New Features in v2.0

### Security Enhancements
- **Path Traversal Protection**: Prevents directory traversal attacks
- **Input Validation & Sanitization**: All inputs are validated and sanitized
- **Rate Limiting**: Built-in protection against abuse
- **Content Validation**: Detects and blocks suspicious content
- **Secure Logging**: Structured logging with sensitive data protection
- **Non-root Container**: Runs as non-privileged user in Docker

### Performance & Reliability
- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Health Checks**: Built-in health monitoring endpoints
- **Error Handling**: Comprehensive error handling and recovery
- **Memory Efficiency**: Optimized memory usage
- **Multi-stage Docker Build**: Smaller, more secure container images

## 🚀 Quick Start

**Want to get started in 30 seconds?** See [QUICKSTART.md](QUICKSTART.md)

```bash
git clone https://github.com/B4DCATs/openvpn_exporter.git
cd openvpn_exporter
./run.sh
```

## 📋 Supported OpenVPN Status Formats

The exporter supports all OpenVPN status file formats:
- **Client statistics** (OpenVPN STATISTICS format)
- **Server statistics v2** (comma-delimited)
- **Server statistics v3** (tab-delimited)
- **OpenVPN CLIENT LIST** format

## 🐳 Docker

### Pre-built Image (Recommended)

Use the pre-built image from GitHub Container Registry:

```bash
docker run -d \
  --name openvpn-exporter \
  -p 9176:9176 \
  -v /var/log/openvpn:/var/log/openvpn:ro \
  -v /etc/openvpn:/etc/openvpn:ro \
  -e STATUS_PATHS="/var/log/openvpn/status.log" \
  ghcr.io/b4dcats/openvpn_exporter:latest
```

### Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/B4DCATs/openvpn_exporter.git
cd openvpn_exporter

# Start exporter
docker-compose up -d

# Check status
curl http://localhost:9176/metrics
```

### Build from Source

```bash
# Clone and build
git clone https://github.com/B4DCATs/openvpn_exporter.git
cd openvpn_exporter
docker build -t openvpn-exporter:v2.0 .

# Run
docker run -d \
  --name openvpn-exporter \
  -p 9176:9176 \
  -v /var/log/openvpn:/var/log/openvpn:ro \
  -e STATUS_PATHS="/var/log/openvpn/status.log" \
  openvpn-exporter:v2.0
```

Metrics should be available at http://localhost:9176/metrics.

## 📊 Metrics Examples

### Client Statistics

For client status files, the exporter generates metrics that may look like this:

```
openvpn_client_auth_read_bytes_total{status_path="..."} 3.08854782e+08
openvpn_client_post_compress_bytes_total{status_path="..."} 4.5446864e+07
openvpn_client_post_decompress_bytes_total{status_path="..."} 2.16965355e+08
openvpn_client_pre_compress_bytes_total{status_path="..."} 4.538819e+07
openvpn_client_pre_decompress_bytes_total{status_path="..."} 1.62596168e+08
openvpn_client_tcp_udp_read_bytes_total{status_path="..."} 2.92806201e+08
openvpn_client_tcp_udp_write_bytes_total{status_path="..."} 1.97558969e+08
openvpn_client_tun_tap_read_bytes_total{status_path="..."} 1.53789941e+08
openvpn_client_tun_tap_write_bytes_total{status_path="..."} 3.08764078e+08
openvpn_status_update_time_seconds{status_path="..."} 1.490092749e+09
openvpn_up{status_path="..."} 1
```

### Server Statistics

For server status files (both version 2 and 3), the exporter generates metrics that may look like this:

```
openvpn_server_client_received_bytes_total{common_name="...",connection_time="...",real_address="...",status_path="...",username="...",virtual_address="..."} 139583
openvpn_server_client_sent_bytes_total{common_name="...",connection_time="...",real_address="...",status_path="...",username="...",virtual_address="..."} 710764
openvpn_server_route_last_reference_time_seconds{common_name="...",real_address="...",status_path="...",virtual_address="..."} 1.493018841e+09
openvpn_status_update_time_seconds{status_path="..."} 1.490089154e+09
openvpn_up{status_path="..."} 1
openvpn_server_connected_clients 1
```

## 🔧 Usage

Usage of openvpn_exporter:

```sh
  -openvpn.status_paths string
    	Paths at which OpenVPN places its status files. (default "examples/client.status,examples/server2.status,examples/server3.status")
  -web.listen-address string
    	Address to listen on for web interface and telemetry. (default ":9176")
  -web.telemetry-path string
    	Path under which to expose metrics. (default "/metrics")
  -ignore.individuals bool
        If ignoring metrics for individuals (default false)
```

Example:

```sh
openvpn_exporter -openvpn.status_paths /etc/openvpn/openvpn-status.log
```

## 📈 Monitoring with Prometheus and Grafana

### Prometheus Configuration

Add to Prometheus configuration (`prometheus.yml`):

```yaml
scrape_configs:
  - job_name: 'openvpn-metrics'
    static_configs:
      - targets: ['YOUR_SERVER_IP:9176']
    scrape_interval: 30s
```

### Grafana Setup

1. Import dashboard from `dashboard.json.tmp` file
2. Configure Prometheus as data source
3. Dashboard will display:
   - OpenVPN server status
   - Number of connected clients
   - Traffic per client
   - Top active users

## 🛠️ Development

### Requirements
- Python 3.11+
- Docker
- Git

### Development Setup

```bash
# Clone repository
git clone https://github.com/B4DCATs/openvpn_exporter.git
cd openvpn_exporter

# Install dependencies
pip install -r requirements.txt

# Run in development mode
python openvpn_exporter.py --openvpn.status_paths examples/client.status,examples/server2.status,examples/server3.status
```

## 🤝 Contributing

We welcome contributions! Please read our [contributing guidelines](CONTRIBUTING.md) before submitting a pull request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💬 Support

- 🐛 [Report a bug](https://github.com/B4DCATs/openvpn_exporter/issues)
- 💡 [Request a feature](https://github.com/B4DCATs/openvpn_exporter/issues)
- 💬 [Discord server](https://discord.gg/VMKdhujjCW)

## 🔗 Useful Links

- [OpenVPN](https://openvpn.net/)
- [Prometheus](https://prometheus.io/)
- [Grafana](https://grafana.com/)
- [Docker](https://www.docker.com/)
