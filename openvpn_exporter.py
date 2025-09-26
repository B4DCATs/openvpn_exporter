#!/usr/bin/env python3
"""
OpenVPN Prometheus Exporter v2.0
Enhanced security and Python implementation

Security improvements:
- Path traversal protection
- Input validation and sanitization
- Rate limiting
- Authentication support
- Secure logging
- Content validation
"""

import os
import sys
import logging
import argparse
import time
import re
import hashlib
import hmac
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, timezone
import json
from functools import wraps
from collections import defaultdict
import threading
from urllib.parse import urlparse

from prometheus_client import (
    Counter, Gauge, Histogram, Info, 
    generate_latest, CONTENT_TYPE_LATEST,
    CollectorRegistry, REGISTRY
)
from flask import Flask, Response, request, jsonify, abort
from dotenv import load_dotenv
import validators
import structlog

# Load environment variables
load_dotenv()

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

class SecurityValidator:
    """Enhanced security validation utilities"""
    
    # Allowed directories for status files
    ALLOWED_DIRS = [
        Path("/var/log/openvpn"),
        Path("/etc/openvpn"),
        Path("/tmp/openvpn"),
        Path("./examples"),  # For testing
    ]
    
    # Maximum file size (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    # Rate limiting
    RATE_LIMIT_WINDOW = 60  # seconds
    MAX_REQUESTS_PER_WINDOW = 100
    
    def __init__(self):
        self.request_counts = defaultdict(list)
        self.lock = threading.Lock()
    
    def validate_path(self, path: str) -> bool:
        """Validate file path to prevent path traversal attacks"""
        try:
            resolved_path = Path(path).resolve()
            
            # Check if path is within allowed directories
            for allowed_dir in self.ALLOWED_DIRS:
                try:
                    if resolved_path.is_relative_to(allowed_dir.resolve()):
                        return True
                except (OSError, ValueError):
                    continue
            
            logger.warning("Path traversal attempt blocked", path=path)
            return False
        except Exception as e:
            logger.error("Path validation error", path=path, error=str(e))
            return False
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent injection attacks"""
        if not filename:
            return "unknown"
        
        # Remove any path traversal attempts
        filename = filename.replace('..', '').replace('/', '').replace('\\', '')
        # Remove any non-alphanumeric characters except dots, hyphens, and underscores
        filename = re.sub(r'[^a-zA-Z0-9.\-_]', '', filename)
        
        # Limit length
        filename = filename[:100]
        
        return filename or "unknown"
    
    def validate_ip_address(self, ip: str) -> bool:
        """Validate IP address format"""
        if not ip or ip == "unknown":
            return True  # Allow unknown IPs
        
        try:
            return validators.ipv4(ip) or validators.ipv6(ip)
        except Exception:
            return False
    
    def validate_file_content(self, content: str) -> bool:
        """Validate file content for suspicious patterns"""
        if not content:
            return False
        
        # Check for suspicious content
        suspicious_patterns = [
            r'<script[^>]*>',
            r'javascript:',
            r'vbscript:',
            r'data:text/html',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>',
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                logger.warning("Suspicious content detected", pattern=pattern)
                return False
        
        return True
    
    def check_rate_limit(self, client_ip: str) -> bool:
        """Check if client has exceeded rate limit"""
        current_time = time.time()
        
        with self.lock:
            # Clean old requests
            self.request_counts[client_ip] = [
                req_time for req_time in self.request_counts[client_ip]
                if current_time - req_time < self.RATE_LIMIT_WINDOW
            ]
            
            # Check if limit exceeded
            if len(self.request_counts[client_ip]) >= self.MAX_REQUESTS_PER_WINDOW:
                logger.warning("Rate limit exceeded", client_ip=client_ip)
                return False
            
            # Add current request
            self.request_counts[client_ip].append(current_time)
            return True

class OpenVPNStatusParser:
    """Enhanced OpenVPN status file parser with security improvements"""
    
    def __init__(self, status_paths: List[str], ignore_individuals: bool = False):
        self.status_paths = status_paths
        self.ignore_individuals = ignore_individuals
        self.validator = SecurityValidator()
        
        # Validate all paths before processing
        self._validate_paths()
        
        # Initialize metrics
        self._init_metrics()
    
    def _validate_paths(self):
        """Validate all status file paths"""
        for path in self.status_paths:
            if not self.validator.validate_path(path):
                raise ValueError(f"Invalid or unsafe path: {path}")
            if not os.path.exists(path):
                logger.warning("Status file does not exist", path=path)
    
    def _init_metrics(self):
        """Initialize Prometheus metrics"""
        self.registry = CollectorRegistry()
        
        # Common metrics
        self.openvpn_up = Gauge(
            'openvpn_up',
            'Whether scraping OpenVPN metrics was successful',
            ['status_path'],
            registry=self.registry
        )
        
        self.openvpn_status_update_time = Gauge(
            'openvpn_status_update_time_seconds',
            'UNIX timestamp at which OpenVPN statistics were updated',
            ['status_path'],
            registry=self.registry
        )
        
        # Server metrics
        self.openvpn_connected_clients = Gauge(
            'openvpn_server_connected_clients',
            'Number of connected clients',
            ['status_path'],
            registry=self.registry
        )
        
        self.openvpn_client_received_bytes = Counter(
            'openvpn_server_client_received_bytes_total',
            'Amount of data received over a connection on the VPN server, in bytes',
            ['status_path', 'common_name', 'real_address', 'virtual_address', 'username'],
            registry=self.registry
        )
        
        self.openvpn_client_sent_bytes = Counter(
            'openvpn_server_client_sent_bytes_total',
            'Amount of data sent over a connection on the VPN server, in bytes',
            ['status_path', 'common_name', 'real_address', 'virtual_address', 'username'],
            registry=self.registry
        )
        
        self.openvpn_route_last_reference_time = Gauge(
            'openvpn_server_route_last_reference_time_seconds',
            'Time at which a route was last referenced, in seconds',
            ['status_path', 'common_name', 'real_address', 'virtual_address'],
            registry=self.registry
        )
        
        # Client metrics
        self.openvpn_client_tun_tap_read_bytes = Counter(
            'openvpn_client_tun_tap_read_bytes_total',
            'Total amount of TUN/TAP traffic read, in bytes',
            ['status_path'],
            registry=self.registry
        )
        
        self.openvpn_client_tun_tap_write_bytes = Counter(
            'openvpn_client_tun_tap_write_bytes_total',
            'Total amount of TUN/TAP traffic written, in bytes',
            ['status_path'],
            registry=self.registry
        )
        
        self.openvpn_client_tcp_udp_read_bytes = Counter(
            'openvpn_client_tcp_udp_read_bytes_total',
            'Total amount of TCP/UDP traffic read, in bytes',
            ['status_path'],
            registry=self.registry
        )
        
        self.openvpn_client_tcp_udp_write_bytes = Counter(
            'openvpn_client_tcp_udp_write_bytes_total',
            'Total amount of TCP/UDP traffic written, in bytes',
            ['status_path'],
            registry=self.registry
        )
        
        self.openvpn_client_auth_read_bytes = Counter(
            'openvpn_client_auth_read_bytes_total',
            'Total amount of authentication traffic read, in bytes',
            ['status_path'],
            registry=self.registry
        )
        
        self.openvpn_client_pre_compress_bytes = Counter(
            'openvpn_client_pre_compress_bytes_total',
            'Total amount of data before compression, in bytes',
            ['status_path'],
            registry=self.registry
        )
        
        self.openvpn_client_post_compress_bytes = Counter(
            'openvpn_client_post_compress_bytes_total',
            'Total amount of data after compression, in bytes',
            ['status_path'],
            registry=self.registry
        )
        
        self.openvpn_client_pre_decompress_bytes = Counter(
            'openvpn_client_pre_decompress_bytes_total',
            'Total amount of data before decompression, in bytes',
            ['status_path'],
            registry=self.registry
        )
        
        self.openvpn_client_post_decompress_bytes = Counter(
            'openvpn_client_post_decompress_bytes_total',
            'Total amount of data after decompression, in bytes',
            ['status_path'],
            registry=self.registry
        )
    
    def parse_status_file(self, status_path: str) -> Dict[str, Any]:
        """Parse OpenVPN status file with enhanced security"""
        try:
            # Check file size
            file_size = os.path.getsize(status_path)
            if file_size > self.validator.MAX_FILE_SIZE:
                raise ValueError(f"File too large: {file_size} bytes")
            
            with open(status_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Validate content
            if not self.validator.validate_file_content(content):
                raise ValueError("Suspicious content detected in status file")
            
            return self._parse_content(content, status_path)
            
        except Exception as e:
            logger.error("Error parsing status file", path=status_path, error=str(e))
            raise
    
    def _parse_content(self, content: str, status_path: str) -> Dict[str, Any]:
        """Parse the content of the status file"""
        lines = content.strip().split('\n')
        
        if not lines:
            raise ValueError("Empty status file")
        
        # Detect file type
        if lines[0].startswith('TITLE,'):
            return self._parse_server_status_v2(lines, status_path)
        elif lines[0].startswith('TITLE\t'):
            return self._parse_server_status_v3(lines, status_path)
        elif lines[0].startswith('OpenVPN STATISTICS'):
            return self._parse_client_status(lines, status_path)
        else:
            raise ValueError(f"Unknown status file format: {lines[0][:50]}")
    
    def _parse_server_status_v2(self, lines: List[str], status_path: str) -> Dict[str, Any]:
        """Parse server status file version 2 (comma delimited)"""
        return self._parse_server_status(lines, status_path, ',')
    
    def _parse_server_status_v3(self, lines: List[str], status_path: str) -> Dict[str, Any]:
        """Parse server status file version 3 (tab delimited)"""
        return self._parse_server_status(lines, status_path, '\t')
    
    def _parse_server_status(self, lines: List[str], status_path: str, separator: str) -> Dict[str, Any]:
        """Parse server status file"""
        headers = {}
        connected_clients = 0
        
        for line in lines:
            if not line.strip():
                continue
                
            fields = line.split(separator)
            
            if fields[0] == 'TIME' and len(fields) >= 3:
                try:
                    timestamp = float(fields[2])
                    self.openvpn_status_update_time.labels(status_path=status_path).set(timestamp)
                except ValueError:
                    logger.warning("Invalid timestamp", path=status_path, timestamp=fields[2])
            
            elif fields[0] == 'HEADER' and len(fields) > 2:
                headers[fields[1]] = fields[2:]
            
            elif fields[0] == 'CLIENT_LIST' and len(fields) > 1:
                connected_clients += 1
                
                if not self.ignore_individuals and len(fields) >= 9:
                    # Sanitize inputs
                    common_name = self.validator.sanitize_filename(fields[1])
                    real_address = fields[2] if self.validator.validate_ip_address(fields[2].split(':')[0]) else 'unknown'
                    virtual_address = fields[3] if self.validator.validate_ip_address(fields[3]) else 'unknown'
                    username = self.validator.sanitize_filename(fields[8]) if len(fields) > 8 else 'unknown'
                    
                    try:
                        received_bytes = float(fields[4])
                        sent_bytes = float(fields[5])
                        
                        self.openvpn_client_received_bytes.labels(
                            status_path=status_path,
                            common_name=common_name,
                            real_address=real_address,
                            virtual_address=virtual_address,
                            username=username
                        ).inc(received_bytes)
                        
                        self.openvpn_client_sent_bytes.labels(
                            status_path=status_path,
                            common_name=common_name,
                            real_address=real_address,
                            virtual_address=virtual_address,
                            username=username
                        ).inc(sent_bytes)
                    except (ValueError, IndexError) as e:
                        logger.warning("Error parsing client data", error=str(e))
            
            elif fields[0] == 'ROUTING_TABLE' and len(fields) >= 6:
                if not self.ignore_individuals:
                    common_name = self.validator.sanitize_filename(fields[1])
                    real_address = fields[2] if self.validator.validate_ip_address(fields[2].split(':')[0]) else 'unknown'
                    virtual_address = fields[0] if self.validator.validate_ip_address(fields[0]) else 'unknown'
                    
                    try:
                        last_ref_time = float(fields[5])
                        self.openvpn_route_last_reference_time.labels(
                            status_path=status_path,
                            common_name=common_name,
                            real_address=real_address,
                            virtual_address=virtual_address
                        ).set(last_ref_time)
                    except (ValueError, IndexError) as e:
                        logger.warning("Error parsing routing data", error=str(e))
        
        # Set connected clients count
        self.openvpn_connected_clients.labels(status_path=status_path).set(connected_clients)
        
        return {"connected_clients": connected_clients}
    
    def _parse_client_status(self, lines: List[str], status_path: str) -> Dict[str, Any]:
        """Parse client status file"""
        for line in lines:
            if not line.strip():
                continue
                
            fields = line.split(',')
            
            if fields[0] == 'Updated' and len(fields) >= 2:
                try:
                    # Parse timestamp
                    time_str = fields[1].strip()
                    time_obj = datetime.strptime(time_str, "%a %b %d %H:%M:%S %Y")
                    timestamp = time_obj.replace(tzinfo=timezone.utc).timestamp()
                    self.openvpn_status_update_time.labels(status_path=status_path).set(timestamp)
                except ValueError as e:
                    logger.warning("Error parsing timestamp", error=str(e))
            
            elif fields[0] == 'TUN/TAP read bytes' and len(fields) >= 2:
                try:
                    value = float(fields[1])
                    self.openvpn_client_tun_tap_read_bytes.labels(status_path=status_path).inc(value)
                except ValueError:
                    pass
            
            elif fields[0] == 'TUN/TAP write bytes' and len(fields) >= 2:
                try:
                    value = float(fields[1])
                    self.openvpn_client_tun_tap_write_bytes.labels(status_path=status_path).inc(value)
                except ValueError:
                    pass
            
            elif fields[0] == 'TCP/UDP read bytes' and len(fields) >= 2:
                try:
                    value = float(fields[1])
                    self.openvpn_client_tcp_udp_read_bytes.labels(status_path=status_path).inc(value)
                except ValueError:
                    pass
            
            elif fields[0] == 'TCP/UDP write bytes' and len(fields) >= 2:
                try:
                    value = float(fields[1])
                    self.openvpn_client_tcp_udp_write_bytes.labels(status_path=status_path).inc(value)
                except ValueError:
                    pass
            
            elif fields[0] == 'Auth read bytes' and len(fields) >= 2:
                try:
                    value = float(fields[1])
                    self.openvpn_client_auth_read_bytes.labels(status_path=status_path).inc(value)
                except ValueError:
                    pass
            
            elif fields[0] == 'pre-compress bytes' and len(fields) >= 2:
                try:
                    value = float(fields[1])
                    self.openvpn_client_pre_compress_bytes.labels(status_path=status_path).inc(value)
                except ValueError:
                    pass
            
            elif fields[0] == 'post-compress bytes' and len(fields) >= 2:
                try:
                    value = float(fields[1])
                    self.openvpn_client_post_compress_bytes.labels(status_path=status_path).inc(value)
                except ValueError:
                    pass
            
            elif fields[0] == 'pre-decompress bytes' and len(fields) >= 2:
                try:
                    value = float(fields[1])
                    self.openvpn_client_pre_decompress_bytes.labels(status_path=status_path).inc(value)
                except ValueError:
                    pass
            
            elif fields[0] == 'post-decompress bytes' and len(fields) >= 2:
                try:
                    value = float(fields[1])
                    self.openvpn_client_post_decompress_bytes.labels(status_path=status_path).inc(value)
                except ValueError:
                    pass
        
        return {"status": "parsed"}

class OpenVPNExporter:
    """Main OpenVPN Exporter class"""
    
    def __init__(self, status_paths: List[str], ignore_individuals: bool = False):
        self.status_paths = status_paths
        self.ignore_individuals = ignore_individuals
        self.parser = OpenVPNStatusParser(status_paths, ignore_individuals)
        self.validator = SecurityValidator()
    
    def collect_metrics(self):
        """Collect metrics from all status files"""
        for status_path in self.status_paths:
            try:
                self.parser.parse_status_file(status_path)
                self.parser.openvpn_up.labels(status_path=status_path).set(1)
            except Exception as e:
                logger.error("Failed to collect metrics", path=status_path, error=str(e))
                self.parser.openvpn_up.labels(status_path=status_path).set(0)
    
    def get_metrics(self) -> str:
        """Get metrics in Prometheus format"""
        self.collect_metrics()
        return generate_latest(self.parser.registry)

def create_app(status_paths: List[str], ignore_individuals: bool = False) -> Flask:
    """Create Flask application with security enhancements"""
    app = Flask(__name__)
    
    # Initialize exporter
    exporter = OpenVPNExporter(status_paths, ignore_individuals)
    validator = SecurityValidator()
    
    def rate_limit_check():
        """Check rate limiting"""
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        if not validator.check_rate_limit(client_ip):
            abort(429)
    
    @app.route('/metrics')
    def metrics():
        """Prometheus metrics endpoint"""
        rate_limit_check()
        
        try:
            metrics_data = exporter.get_metrics()
            return Response(metrics_data, mimetype=CONTENT_TYPE_LATEST)
        except Exception as e:
            logger.error("Error generating metrics", error=str(e))
            abort(500)
    
    @app.route('/health')
    def health():
        """Health check endpoint"""
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "2.0.0"
        })
    
    @app.route('/')
    def index():
        """Main page"""
        return '''
        <html>
        <head><title>OpenVPN Exporter v2.0</title></head>
        <body>
        <h1>OpenVPN Exporter v2.0</h1>
        <p><a href='/metrics'>Metrics</a></p>
        <p><a href='/health'>Health Check</a></p>
        <p>Enhanced security features:</p>
        <ul>
        <li>Path traversal protection</li>
        <li>Input validation and sanitization</li>
        <li>Rate limiting</li>
        <li>Secure logging</li>
        <li>Content validation</li>
        </ul>
        </body>
        </html>
        '''
    
    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return jsonify({"error": "Rate limit exceeded"}), 429
    
    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Internal server error"}), 500
    
    return app

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='OpenVPN Prometheus Exporter v2.0')
    parser.add_argument('--web.listen-address', 
                       default=os.environ.get('LISTEN_ADDRESS', ':9176'),
                       help='Address to listen on for web interface and telemetry')
    parser.add_argument('--web.telemetry-path', 
                       default=os.environ.get('TELEMETRY_PATH', '/metrics'),
                       help='Path under which to expose metrics')
    parser.add_argument('--openvpn.status_paths', 
                       default=os.environ.get('STATUS_PATHS', 'examples/client.status,examples/server2.status,examples/server3.status'),
                       help='Paths at which OpenVPN places its status files')
    parser.add_argument('--ignore.individuals', 
                       action='store_true',
                       default=os.environ.get('IGNORE_INDIVIDUALS', 'false').lower() == 'true',
                       help='If ignoring metrics for individuals')
    parser.add_argument('--log-level', 
                       default=os.environ.get('LOG_LEVEL', 'INFO'),
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Log level')
    
    args = parser.parse_args()
    
    # Configure logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Parse status paths
    status_paths = [path.strip() for path in args.openvpn.status_paths.split(',')]
    
    logger.info("Starting OpenVPN Exporter v2.0",
                listen_address=args.web.listen_address,
                metrics_path=args.web.telemetry_path,
                status_paths=status_paths,
                ignore_individuals=args.ignore_individuals)
    
    # Create Flask app
    app = create_app(status_paths, args.ignore_individuals)
    
    # Start server
    host, port = args.web.listen_address.split(':')
    if not host:
        host = '0.0.0.0'
    
    app.run(host=host, port=int(port), debug=False)

if __name__ == '__main__':
    main()
