# OpenVPN Prometheus Exporter v2.0

[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://hub.docker.com/r/b4dcats/openvpn_exporter)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg?style=for-the-badge)](LICENSE)
[![Discord](https://img.shields.io/discord/VMKdhujjCW?style=for-the-badge&logo=discord&logoColor=white&label=Discord)](https://discord.gg/VMKdhujjCW)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/B4DCATs/openvpn_exporter)
[![GitHub stars](https://img.shields.io/github/stars/B4DCATs/openvpn_exporter?style=for-the-badge&logo=github&logoColor=white)](https://github.com/B4DCATs/openvpn_exporter/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/B4DCATs/openvpn_exporter?style=for-the-badge&logo=github&logoColor=white)](https://github.com/B4DCATs/openvpn_exporter/network)

**Enhanced Python implementation with improved security features**

This repository provides a secure Prometheus metrics exporter for [OpenVPN](https://openvpn.net/). The v2.0 release is a complete rewrite in Python with significant security improvements and enhanced functionality.

## 📚 Documentation

- [🇷🇺](docs/ru/README.md)
- [🇺🇸](docs/en/README.md)

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

**Хотите запустить за 30 секунд?** Смотрите [QUICKSTART.md](QUICKSTART.md)

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

## Exposed metrics example

### Client statistics

For clients status files, the exporter generates metrics that may look
like this:

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

### Server statistics

For server status files (both version 2 and 3), the exporter generates
metrics that may look like this:

```
openvpn_server_client_received_bytes_total{common_name="...",connection_time="...",real_address="...",status_path="...",username="...",virtual_address="..."} 139583
openvpn_server_client_sent_bytes_total{common_name="...",connection_time="...",real_address="...",status_path="...",username="...",virtual_address="..."} 710764
openvpn_server_route_last_reference_time_seconds{common_name="...",real_address="...",status_path="...",virtual_address="..."} 1.493018841e+09
openvpn_status_update_time_seconds{status_path="..."} 1.490089154e+09
openvpn_up{status_path="..."} 1
openvpn_server_connected_clients 1
```

## Usage

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

E.g:

```sh
openvpn_exporter -openvpn.status_paths /etc/openvpn/openvpn-status.log
```

## 🐳 Docker

### Pre-built Image (Recommended)

Use the pre-built image from GitHub Container Registry:

```bash
docker run -d \
  --name openvpn-exporter \
  -p 9176:9176 \
  -v /var/log/openvpn:/var/log/openvpn:ro \
  -v /etc/openvpn:/etc/openvpn:ro \
  -e STATUS_PATHS="/var/log/openvpn/server.status" \
  ghcr.io/b4dcats/openvpn_exporter:latest
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
  -e STATUS_PATHS="/var/log/openvpn/server.status" \
  openvpn-exporter:v2.0
```

Metrics should be available at http://localhost:9176/metrics.

## 📄 License

This project is licensed under the **Apache License 2.0** - see the [LICENSE](LICENSE) file for details.

### What this means:
- ✅ **Free to use** - Commercial and personal use allowed
- ✅ **Free to modify** - You can change the code
- ✅ **Free to distribute** - You can share and redistribute
- ✅ **Patent protection** - Protection against patent lawsuits
- ⚠️ **Must include license** - Include the Apache 2.0 license with distributions
- ⚠️ **Must credit changes** - Indicate if you modified the files

## 🔗 Useful Links

- [OpenVPN](https://openvpn.net/)
- [Prometheus](https://prometheus.io/)
- [Grafana](https://grafana.com/)
- [Docker](https://www.docker.com/)
- [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)
