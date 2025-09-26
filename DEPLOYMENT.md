# Deployment Guide - OpenVPN Prometheus Exporter v2.0

## Quick Start

### 1. Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-org/openvpn_exporter.git
cd openvpn_exporter

# Build the image
docker build -t openvpn-exporter:v2.0 .

# Run with your OpenVPN status files
docker run -d \
  --name openvpn-exporter \
  -p 9176:9176 \
  -v /var/log/openvpn:/var/log/openvpn:ro \
  -v /etc/openvpn:/etc/openvpn:ro \
  openvpn-exporter:v2.0 \
  --openvpn.status_paths /var/log/openvpn/server.status
```

### 2. Using Docker Compose

```bash
# Start with docker-compose
docker-compose up -d

# Check status
docker-compose ps
```

### 3. Using Python

```bash
# Install dependencies
pip install -r requirements.txt

# Run the exporter
python openvpn_exporter.py \
  --openvpn.status_paths /var/log/openvpn/server.status \
  --web.listen-address :9176
```

## Production Deployment

### Prerequisites

1. **OpenVPN Server** with status logging enabled
2. **Prometheus** for metrics collection
3. **Docker** (recommended) or Python 3.11+
4. **Firewall** configured for port 9176

### OpenVPN Configuration

Add these directives to your OpenVPN server configuration:

```bash
# /etc/openvpn/server.conf
status /var/log/openvpn/server.status
status-version 2
status-update 10
```

For client monitoring:
```bash
# /etc/openvpn/client.conf
status /var/log/openvpn/client.status
status-version 2
status-update 10
```

### Docker Deployment

#### 1. Create Docker Network
```bash
docker network create monitoring
```

#### 2. Run the Exporter
```bash
docker run -d \
  --name openvpn-exporter \
  --network monitoring \
  -p 9176:9176 \
  -v /var/log/openvpn:/var/log/openvpn:ro \
  -v /etc/openvpn:/etc/openvpn:ro \
  -e SECRET_KEY="$(openssl rand -base64 32)" \
  -e LOG_LEVEL=INFO \
  openvpn-exporter:v2.0 \
  --openvpn.status_paths /var/log/openvpn/server.status,/var/log/openvpn/client.status
```

#### 3. Verify Deployment
```bash
# Check container status
docker ps | grep openvpn-exporter

# Check logs
docker logs openvpn-exporter

# Test metrics endpoint
curl http://localhost:9176/metrics

# Test health endpoint
curl http://localhost:9176/health
```

### Systemd Service (Python Installation)

#### 1. Create Service File
```bash
sudo tee /etc/systemd/system/openvpn-exporter.service > /dev/null <<EOF
[Unit]
Description=OpenVPN Prometheus Exporter v2.0
After=network.target

[Service]
Type=simple
User=openvpn-exporter
Group=openvpn-exporter
WorkingDirectory=/opt/openvpn-exporter
ExecStart=/opt/openvpn-exporter/venv/bin/python openvpn_exporter.py
Restart=always
RestartSec=5

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/openvpn-exporter

# Environment
Environment=SECRET_KEY=your-secret-key-here
Environment=LOG_LEVEL=INFO

[Install]
WantedBy=multi-user.target
EOF
```

#### 2. Create User and Directory
```bash
# Create user
sudo useradd -r -s /bin/false openvpn-exporter

# Create directory
sudo mkdir -p /opt/openvpn-exporter
sudo chown openvpn-exporter:openvpn-exporter /opt/openvpn-exporter

# Copy files
sudo cp openvpn_exporter.py /opt/openvpn-exporter/
sudo cp requirements.txt /opt/openvpn-exporter/
sudo chown openvpn-exporter:openvpn-exporter /opt/openvpn-exporter/*
```

#### 3. Install Dependencies
```bash
cd /opt/openvpn-exporter
sudo -u openvpn-exporter python -m venv venv
sudo -u openvpn-exporter venv/bin/pip install -r requirements.txt
```

#### 4. Enable and Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable openvpn-exporter
sudo systemctl start openvpn-exporter
sudo systemctl status openvpn-exporter
```

## Kubernetes Deployment

### 1. Create Namespace
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: monitoring
```

### 2. Create ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: openvpn-exporter-config
  namespace: monitoring
data:
  status_paths: "/var/log/openvpn/server.status"
  listen_address: ":9176"
  log_level: "INFO"
```

### 3. Create Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openvpn-exporter
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: openvpn-exporter
  template:
    metadata:
      labels:
        app: openvpn-exporter
    spec:
      containers:
      - name: openvpn-exporter
        image: openvpn-exporter:v2.0
        ports:
        - containerPort: 9176
        env:
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: openvpn-exporter-secrets
              key: secret-key
        volumeMounts:
        - name: openvpn-logs
          mountPath: /var/log/openvpn
          readOnly: true
        - name: openvpn-config
          mountPath: /etc/openvpn
          readOnly: true
      volumes:
      - name: openvpn-logs
        hostPath:
          path: /var/log/openvpn
      - name: openvpn-config
        hostPath:
          path: /etc/openvpn
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
```

### 4. Create Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: openvpn-exporter
  namespace: monitoring
spec:
  selector:
    app: openvpn-exporter
  ports:
  - port: 9176
    targetPort: 9176
  type: ClusterIP
```

## Monitoring Setup

### Prometheus Configuration

Add to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'openvpn-exporter'
    static_configs:
      - targets: ['openvpn-exporter:9176']
    scrape_interval: 30s
    metrics_path: /metrics
    scrape_timeout: 10s
```

### Grafana Dashboard

Import the dashboard JSON or create panels for:
- OpenVPN server status
- Connected clients count
- Traffic metrics
- Error rates

### Alerting Rules

```yaml
groups:
  - name: openvpn
    rules:
      - alert: OpenVPNDown
        expr: openvpn_up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "OpenVPN exporter is down"
          description: "OpenVPN exporter has been down for more than 1 minute"
          
      - alert: OpenVPNNoClients
        expr: openvpn_server_connected_clients == 0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "No OpenVPN clients connected"
          description: "No OpenVPN clients have been connected for more than 5 minutes"
```

## Security Configuration

### Firewall Rules

```bash
# Allow Prometheus to scrape metrics
iptables -A INPUT -p tcp --dport 9176 -s 192.168.1.0/24 -j ACCEPT

# Allow local access
iptables -A INPUT -p tcp --dport 9176 -s 127.0.0.1 -j ACCEPT

# Block other access
iptables -A INPUT -p tcp --dport 9176 -j DROP
```

### SSL/TLS Configuration

For production, use a reverse proxy with SSL:

```nginx
server {
    listen 443 ssl;
    server_name monitoring.your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location /metrics {
        proxy_pass http://localhost:9176;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Troubleshooting

### Common Issues

#### 1. Permission Denied
```bash
# Check file permissions
ls -la /var/log/openvpn/server.status

# Fix permissions
sudo chmod 644 /var/log/openvpn/server.status
sudo chown root:root /var/log/openvpn/server.status
```

#### 2. Container Won't Start
```bash
# Check logs
docker logs openvpn-exporter

# Check container status
docker ps -a | grep openvpn-exporter
```

#### 3. No Metrics
```bash
# Test status file
cat /var/log/openvpn/server.status

# Test metrics endpoint
curl -v http://localhost:9176/metrics
```

#### 4. Rate Limiting Issues
```bash
# Check rate limit settings
docker exec openvpn-exporter env | grep RATE_LIMIT

# Adjust rate limits
docker run -e MAX_REQUESTS_PER_WINDOW=200 openvpn-exporter:v2.0
```

### Log Analysis

```bash
# Monitor logs in real-time
docker logs -f openvpn-exporter

# Filter for errors
docker logs openvpn-exporter 2>&1 | grep ERROR

# Check rate limiting
docker logs openvpn-exporter 2>&1 | grep "Rate limit"
```

## Performance Tuning

### Resource Limits

```yaml
# Docker Compose
services:
  openvpn-exporter:
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.5'
        reservations:
          memory: 128M
          cpus: '0.25'
```

### Scaling

For high-traffic environments:

```yaml
# Kubernetes HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: openvpn-exporter-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: openvpn-exporter
  minReplicas: 1
  maxReplicas: 3
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Backup and Recovery

### Backup Configuration
```bash
# Backup configuration files
tar -czf openvpn-exporter-backup.tar.gz \
  docker-compose.yml \
  prometheus.yml \
  .env
```

### Recovery Procedure
```bash
# Restore from backup
tar -xzf openvpn-exporter-backup.tar.gz

# Restart services
docker-compose up -d
```

## Maintenance

### Regular Tasks

1. **Update Dependencies**
   ```bash
   pip install --upgrade -r requirements.txt
   docker build --no-cache -t openvpn-exporter:v2.0 .
   ```

2. **Monitor Logs**
   ```bash
   # Check for errors
   docker logs openvpn-exporter | grep ERROR
   ```

3. **Verify Metrics**
   ```bash
   # Test metrics endpoint
   curl http://localhost:9176/metrics | grep openvpn_up
   ```

4. **Security Updates**
   ```bash
   # Update base image
   docker pull python:3.11-slim
   docker build -t openvpn-exporter:v2.0 .
   ```

### Health Checks

```bash
# Automated health check script
#!/bin/bash
HEALTH_URL="http://localhost:9176/health"
METRICS_URL="http://localhost:9176/metrics"

# Check health endpoint
if ! curl -f $HEALTH_URL > /dev/null 2>&1; then
    echo "Health check failed"
    exit 1
fi

# Check metrics endpoint
if ! curl -f $METRICS_URL > /dev/null 2>&1; then
    echo "Metrics endpoint failed"
    exit 1
fi

echo "All checks passed"
```
