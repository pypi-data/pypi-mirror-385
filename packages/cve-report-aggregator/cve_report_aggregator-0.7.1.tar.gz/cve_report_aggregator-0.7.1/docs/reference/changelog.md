# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Docker credentials management with two methods: build-time secrets and environment variables
- SOPS encryption support for credentials file (`docker/config.json`)
- Docker BuildKit secret mount for secure credential injection during build
- Entrypoint script with dual authentication support (config.json or env vars)
- Security best practices documentation for credential management
- `.sops.yaml` configuration for encrypting credentials with age key
- Multi-stage Docker build with Alpine Linux base
- Non-root user (cve-aggregator, UID 1001) for container security
- Pre-installed scanning tools in Docker image: Grype, Syft, Trivy, UDS CLI
- Rich terminal output with color-coded tables and progress indicators
- Multi-scanner support (Grype and Trivy)
- SBOM auto-detection and scanning with Grype
- Automatic conversion of Grype reports to CycloneDX format for Trivy
- CVE deduplication across multiple scan reports
- Automatic null CVSS filtering (removes invalid scores)
- CVSS 3.x-based severity selection with `--mode highest-score`
- Scanner source tracking to identify which scanner provided vulnerability data
- Occurrence tracking to count CVE appearances across images
- Click-based CLI with rich-click styling
- Comprehensive test suite with pytest
- Type annotations throughout codebase
- Package installation via pip/pipx
- Docker Compose support

### Changed

- Consolidated Docker credentials documentation into main README.md
- Updated credentials file format to JSON with `username`, `password`, and `registry` fields
- Removed volume mount references from documentation (focus on credential management)
- Simplified credential methods from 4 to 2 (build-time secrets and environment variables)
- Registry is now configurable via credentials file instead of hardcoded

### Removed

- Separate `docker/README.md` file (merged into main README)
- Docker Secrets method (Docker Swarm/Compose secrets)
- Volume-mounted credentials file method
- Support for multiple credential file locations

### Security

- Credentials must be encrypted with SOPS before committing to version control
- Decrypted credential files (\*.dec) are automatically cleaned up after build
- Build-time secrets never appear in Docker image layers
- Container runs as non-root user (UID 1001)
- System pip removed from final image to reduce attack surface
- All dependencies pinned to specific versions in Dockerfile

## [0.1.0] - 2025-01-17

### Added

- Initial release of CVE Report Aggregator
- Basic Grype report aggregation and deduplication
- Command-line interface with Click
- JSON output format with metadata, summary, and vulnerabilities
- Docker support with Dockerfile and docker-compose.yml
- MIT License
- README with usage examples and installation instructions

[0.1.0]: https://github.com/mkm29/cve-report-aggregator/releases/tag/v0.1.0
[unreleased]: https://github.com/mkm29/cve-report-aggregator/compare/v0.1.0...HEAD
