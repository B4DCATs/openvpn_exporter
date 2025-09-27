# Security Guide

This document describes the security features and access control mechanisms available in OpenVPN Prometheus Exporter v2.0.

## 🔒 Access Control

### IP Address Restrictions

You can restrict access to the `/metrics` endpoint to specific IP addresses using the `ALLOWED_IPS` environment variable or `--web.allowed-ips` command line argument.

#### Configuration Methods

**1. Environment Variable**
```bash
export ALLOWED_IPS="192.168.1.100,10.0.0.50,monitoring-server.local"
```

**2. Docker Compose**
```yaml
environment:
  - ALLOWED_IPS=192.168.1.100,10.0.0.50
```

**3. Command Line**
```bash
python openvpn_exporter.py --web.allowed-ips="192.168.1.100,10.0.0.50"
```

#### Examples

```bash
# Allow access from a single IP
ALLOWED_IPS=192.168.1.100

# Allow access from multiple IPs
ALLOWED_IPS=192.168.1.100,10.0.0.50,172.16.0.10

# Allow access from localhost only
ALLOWED_IPS=127.0.0.1,::1

# Allow access from monitoring server hostname
ALLOWED_IPS=monitoring-server.local,prometheus.internal
```

#### How It Works

- The exporter checks the `X-Forwarded-For` header first, then falls back to `remote_addr`
- If `ALLOWED_IPS` is not set, access is allowed from any IP
- If `ALLOWED_IPS` is set, only IPs in the list can access `/metrics`
- Health check endpoint (`/health`) is always accessible for monitoring purposes
- Access attempts from unauthorized IPs are logged with a 403 Forbidden response

## 🛡️ Built-in Security Features

### Rate Limiting
- Built-in protection against abuse and DDoS attacks
- Configurable rate limits per IP address
- Automatic blocking of excessive requests

### Input Validation
- All inputs are validated and sanitized
- Path traversal protection prevents directory traversal attacks
- File size limits prevent resource exhaustion

### Secure Logging
- Structured JSON logging with correlation IDs
- Sensitive data is automatically masked in logs
- Security events are clearly identified

### Container Security
- Non-root container execution
- Read-only file system mounts
- Minimal attack surface with multi-stage Docker builds

## 🔧 Network-Level Security

### Firewall Configuration

**UFW (Ubuntu/Debian)**
```bash
# Allow only specific IPs to access metrics
sudo ufw allow from 192.168.1.100 to any port 9176
sudo ufw allow from 10.0.0.50 to any port 9176

# Or allow from specific network
sudo ufw allow from 192.168.1.0/24 to any port 9176
```

**iptables**
```bash
# Allow only specific IPs
iptables -A INPUT -p tcp --dport 9176 -s 192.168.1.100 -j ACCEPT
iptables -A INPUT -p tcp --dport 9176 -s 10.0.0.50 -j ACCEPT
iptables -A INPUT -p tcp --dport 9176 -j DROP
```

### Reverse Proxy Configuration

**Nginx**
```nginx
server {
    listen 80;
    server_name monitoring.yourdomain.com;
    
    # Restrict access by IP
    allow 192.168.1.100;
    allow 10.0.0.50;
    deny all;
    
    location /metrics {
        proxy_pass http://localhost:9176/metrics;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /health {
        proxy_pass http://localhost:9176/health;
    }
}
```

**Apache**
```apache
<VirtualHost *:80>
    ServerName monitoring.yourdomain.com
    
    <Location "/metrics">
        Require ip 192.168.1.100
        Require ip 10.0.0.50
        ProxyPass http://localhost:9176/metrics
        ProxyPassReverse http://localhost:9176/metrics
    </Location>
    
    <Location "/health">
        ProxyPass http://localhost:9176/health
        ProxyPassReverse http://localhost:9176/health
    </Location>
</VirtualHost>
```

## 🔍 Monitoring and Alerting

### Security Event Monitoring

Monitor your logs for security events:

```bash
# Monitor for access denied events
docker logs openvpn-exporter 2>&1 | grep "Access denied"

# Monitor for rate limiting events
docker logs openvpn-exporter 2>&1 | grep "Rate limit exceeded"
```

### Prometheus Alerting Rules

```yaml
groups:
- name: openvpn_exporter_security
  rules:
  - alert: OpenVPNExporterAccessDenied
    expr: increase(openvpn_exporter_access_denied_total[5m]) > 0
    for: 0m
    labels:
      severity: warning
    annotations:
      summary: "OpenVPN Exporter access denied"
      description: "Someone tried to access metrics from unauthorized IP"
  
  - alert: OpenVPNExporterRateLimit
    expr: increase(openvpn_exporter_rate_limit_total[5m]) > 10
    for: 0m
    labels:
      severity: critical
    annotations:
      summary: "OpenVPN Exporter rate limit exceeded"
      description: "High rate of requests to OpenVPN Exporter"
```

## 🚨 Best Practices

1. **Always use IP restrictions** in production environments
2. **Monitor access logs** regularly for suspicious activity
3. **Use HTTPS** when exposing metrics over the internet
4. **Keep the exporter updated** to the latest version
5. **Use dedicated monitoring networks** when possible
6. **Implement proper firewall rules** at the network level
7. **Use reverse proxies** for additional security layers
8. **Regular security audits** of your monitoring infrastructure

## 🔧 Troubleshooting

### Common Issues

**403 Forbidden when accessing metrics**
- Check if your IP is in the `ALLOWED_IPS` list
- Verify the `X-Forwarded-For` header if behind a proxy
- Check logs for "Access denied" messages

**Health check failing**
- Health endpoint should always be accessible
- Check if the container is running properly
- Verify port 9176 is not blocked by firewall

**Rate limiting issues**
- Check if you're making too many requests
- Adjust rate limiting configuration if needed
- Monitor logs for rate limit events
