# OpenVPN Prometheus Exporter v2.0

## Docker Images

This repository provides pre-built Docker images for the OpenVPN Prometheus Exporter v2.0.

### Available Images

- `ghcr.io/b4dcats/openvpn_exporter:latest` - Latest stable version
- `ghcr.io/b4dcats/openvpn_exporter:v2.0` - Version 2.0
- `ghcr.io/b4dcats/openvpn_exporter:main` - Latest from main branch
- `ghcr.io/b4dcats/openvpn_exporter:v2` - Latest from v2 branch

### Quick Start

```bash
# Pull and run the latest image
docker run -d \
  --name openvpn-exporter \
  -p 9176:9176 \
  -v /var/log/openvpn:/var/log/openvpn:ro \
  -v /etc/openvpn:/etc/openvpn:ro \
  -e STATUS_PATHS="/var/log/openvpn/server.status" \
  ghcr.io/b4dcats/openvpn_exporter:latest
```

### Environment Variables

- `STATUS_PATHS` - Comma-separated paths to OpenVPN status files
- `LISTEN_ADDRESS` - Address to listen on (default: `:9176`)
- `LOG_LEVEL` - Log level (default: `INFO`)
- `IGNORE_INDIVIDUALS` - Ignore individual client metrics (default: `false`)

### Security Features

- Path traversal protection
- Input validation and sanitization
- Rate limiting (100 requests/minute)
- Content validation
- Structured logging
- Non-root container execution

### Documentation

- [Full Documentation](https://github.com/B4DCATs/openvpn_exporter)
- [Quick Start Guide](https://github.com/B4DCATs/openvpn_exporter/blob/v2/QUICKSTART.md)
- [Security Guide](https://github.com/B4DCATs/openvpn_exporter/blob/v2/SECURITY.md)
- [Deployment Guide](https://github.com/B4DCATs/openvpn_exporter/blob/v2/DEPLOYMENT.md)
