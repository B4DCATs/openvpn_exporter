# Configuration Examples

This directory contains various configuration examples for OpenVPN Prometheus Exporter.

## 📁 Directory Structure

```
examples/
├── README.md                    # This file
├── config/                      # Configuration files
│   ├── prometheus.yml.example   # Prometheus configuration
│   ├── openvpn-targets.json.example  # Service discovery targets
│   ├── alert.rules.yml          # Prometheus alerting rules
│   ├── grafana-datasource.yml   # Grafana datasource config
│   └── docker-compose.full.yml  # Complete monitoring stack
└── status/                      # Sample OpenVPN status files
    ├── client.status           # Client statistics example
    ├── server2.status          # Server statistics v2 example
    └── server3.status          # Server statistics v3 example
```

## 🚀 Quick Start

### 1. Basic Setup
```bash
# Copy and customize Prometheus configuration
cp examples/config/prometheus.yml.example prometheus.yml
# Edit prometheus.yml and adjust targets to your OpenVPN servers
```

### 2. Complete Monitoring Stack
```bash
# Run complete stack with Prometheus + Grafana
docker-compose -f examples/config/docker-compose.full.yml up -d
```

### 3. Service Discovery
```bash
# Copy and customize targets file
cp examples/config/openvpn-targets.json.example openvpn-targets.json
# Edit targets and configure Prometheus to use file-based discovery
```

## 📊 Configuration Files

### prometheus.yml.example
Complete Prometheus configuration with examples for:
- Single OpenVPN server monitoring
- Multiple servers monitoring
- Service discovery (DNS and file-based)
- Relabeling and labeling

### openvpn-targets.json.example
File-based service discovery configuration for dynamic target management.

### alert.rules.yml
Comprehensive alerting rules including:
- OpenVPN server availability
- Client connection monitoring
- Security alerts
- Traffic monitoring
- Long-running connections

### grafana-datasource.yml
Automatic provisioning of Prometheus as a datasource in Grafana.

### docker-compose.full.yml
Complete monitoring stack including:
- OpenVPN Exporter
- Prometheus
- Grafana
- Optional AlertManager (commented)

### systemd/
Systemd service installation files for native (non-Docker) deployment:
- `openvpn-exporter.service` - Systemd unit file
- `openvpn-exporter.conf` - Service configuration template
- `install-systemd.sh` - Automated installation script
- `README.md` - Detailed installation and configuration guide

**Quick install:**
```bash
sudo ./examples/systemd/install-systemd.sh
```

## 🔧 Customization

1. **Copy the example files** to your project root or configuration directory
2. **Remove `.example` extension** from copied files
3. **Edit the configuration** according to your environment
4. **Adjust IP addresses, hostnames, and ports** as needed
5. **Test the configuration** before deploying to production

## 📋 Requirements

- Docker and Docker Compose
- OpenVPN server with status files
- Network access between monitoring components
- Sufficient disk space for metrics storage

## 🔒 Security Notes

- Change default passwords in Grafana
- Configure IP restrictions in OpenVPN Exporter
- Use proper firewall rules
- Consider using TLS for external access
- Regularly update container images

## 📚 Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [OpenVPN Documentation](https://openvpn.net/community-resources/)
