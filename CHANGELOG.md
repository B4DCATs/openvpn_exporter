# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.1] - 2025-09-27

### Added
- Quick start script for easy deployment without cloning repository
- Comprehensive Docker Compose example in README
- Reference to [openvpn-install](https://github.com/angristan/openvpn-install) script for OpenVPN server setup
- Health check endpoint for better monitoring
- Improved dashboard with proper time formatting (`dateTimeAsSystem`)

### Changed
- Updated README with better quick start instructions
- Simplified Docker Compose configuration
- Improved Grafana dashboard with correct unit configurations
- Enhanced time display in client table (Login Time column)

### Fixed
- Fixed duplicate count queries in dashboard (servers vs users)
- Corrected timestamp conversion in Prometheus queries
- Fixed time formatting in dashboard tables
- Resolved unit display issues in stat panels

### Security
- Maintained all v2.0 security enhancements
- Non-root container execution
- Input validation and sanitization

## [2.0.0] - 2025-09-26

### Added
- Complete Python rewrite for better security and performance
- Path traversal protection
- Input validation & sanitization
- Rate limiting
- Content validation
- Secure logging with correlation IDs
- Non-root container execution
- Multi-stage Docker build
- Health monitoring endpoints
- Comprehensive error handling

### Changed
- Migrated from Go to Python implementation
- Improved memory efficiency
- Enhanced logging with JSON format
- Better error recovery mechanisms

### Security
- Fixed multiple security vulnerabilities from v1.x
- Implemented defense-in-depth security model
- Added comprehensive input validation
- Enhanced logging security

## [1.x] - Previous versions

### Note
v1.x versions are no longer supported. Please upgrade to v2.0+ for security updates and new features.
