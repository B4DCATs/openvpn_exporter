# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| 1.0.x   | :x:                |

## Security Features in v2.0

### Path Traversal Protection
- All file paths are validated against allowed directories
- Prevents access to sensitive system files like `/etc/passwd`, `/root/.ssh/`
- Configurable allowed directories via environment variables

### Input Validation & Sanitization
- All user inputs are validated and sanitized
- IP address format validation
- Filename sanitization to prevent injection attacks
- Content validation for suspicious patterns (XSS, script injection)

### Rate Limiting
- Built-in rate limiting (100 requests per minute by default)
- Per-IP request tracking
- Configurable limits via environment variables
- Automatic blocking of abusive clients

### Secure Logging
- Structured JSON logging
- Sensitive data protection (no IPs or usernames in logs)
- Correlation IDs for request tracking
- No credentials or tokens in logs

### Container Security
- Non-root user execution
- Minimal base image (Python slim)
- Multi-stage build for smaller attack surface
- Read-only filesystem where possible

## Security Best Practices

### 1. File Permissions
```bash
# Ensure status files have proper permissions
chmod 644 /var/log/openvpn/server.status
chown root:root /var/log/openvpn/server.status
```

### 2. Network Security
```bash
# Use firewall rules to restrict access
iptables -A INPUT -p tcp --dport 9176 -s 192.168.1.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 9176 -j DROP
```

### 3. Environment Variables
```bash
# Configure rate limiting
export RATE_LIMIT_WINDOW=60
export MAX_REQUESTS_PER_WINDOW=50
```

### 4. Docker Security
```bash
# Run with read-only root filesystem
docker run --read-only \
  --tmpfs /tmp \
  -v /var/log/openvpn:/var/log/openvpn:ro \
  openvpn-exporter:v2.0
```

## Reporting a Vulnerability

If you discover a security vulnerability, please follow these steps:

1. **DO NOT** create a public GitHub issue
2. Email security details to: security@your-domain.com
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Security Checklist

### Before Deployment
- [ ] Configure proper file permissions
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Configure log monitoring
- [ ] Test with security tools

### Regular Maintenance
- [ ] Update dependencies regularly
- [ ] Monitor logs for suspicious activity
- [ ] Review access patterns
- [ ] Update security configurations
- [ ] Test backup and recovery

## Security Tools Integration

### OWASP ZAP
```bash
# Test for common vulnerabilities
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t http://localhost:9176/metrics
```

### Bandit Security Linter
```bash
# Check for security issues in code
bandit -r openvpn_exporter.py
```

### Safety Check
```bash
# Check for known vulnerabilities in dependencies
safety check
```

## Incident Response

### If a Security Issue is Detected
1. **Immediate**: Stop the service if necessary
2. **Assess**: Determine scope and impact
3. **Contain**: Isolate affected systems
4. **Investigate**: Gather evidence and logs
5. **Remediate**: Apply fixes and patches
6. **Recover**: Restore service with monitoring
7. **Learn**: Update security measures

### Log Monitoring
```bash
# Monitor for suspicious activity
tail -f /var/log/openvpn-exporter.log | grep -E "(ERROR|WARNING|Rate limit)"
```

## Security Configuration Examples

### Production Environment
```yaml
# docker-compose.yml
services:
  openvpn-exporter:
    environment:
      - LOG_LEVEL=WARNING
      - RATE_LIMIT_WINDOW=60
      - MAX_REQUESTS_PER_WINDOW=50
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
```

### High Security Environment
```bash
# Run with additional security constraints
docker run --security-opt no-new-privileges \
  --read-only \
  --tmpfs /tmp \
  --cap-drop ALL \
  --user 1000:1000 \
  openvpn-exporter:v2.0
```

## Security Updates

### Dependency Updates
```bash
# Check for security updates
pip list --outdated
pip install --upgrade package-name
```

### Container Updates
```bash
# Rebuild with latest base image
docker build --no-cache -t openvpn-exporter:v2.0 .
```

## Contact

For security-related questions or concerns:
- Email: security@your-domain.com
- PGP Key: [Your PGP Key ID]
- Response Time: 24-48 hours for security issues
