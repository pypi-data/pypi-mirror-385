# CVE Report Aggregator

[![Python Version](https://img.shields.io/badge/python-3.12%20%7C%203.13-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/cve-report-aggregator.svg)](https://pypi.org/project/cve-report-aggregator/)
[![PyPI downloads](https://img.shields.io/pypi/dm/cve-report-aggregator.svg)](https://pypi.org/project/cve-report-aggregator/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/mkm29/cve-report-aggregator/blob/main/LICENSE)
[![CI](https://github.com/mkm29/cve-report-aggregator/actions/workflows/test.yml/badge.svg)](https://github.com/mkm29/cve-report-aggregator/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/mkm29/cve-report-aggregator/branch/main/graph/badge.svg?token=mJcMNSlBIM)](https://codecov.io/gh/mkm29/cve-report-aggregator)
[![Latest Release](https://img.shields.io/github/v/release/mkm29/cve-report-aggregator)](https://github.com/mkm29/cve-report-aggregator/releases)
[![Docker](https://img.shields.io/badge/docker-available-blue.svg)](https://github.com/mkm29/cve-report-aggregator/pkgs/container/cve-report-aggregator)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)


A Python package for aggregating and deduplicating Grype and Trivy vulnerability scan reports.

## Features

- **Self-Contained Docker Image**: Includes all scanning tools (Grype, Syft, Trivy, UDS CLI) in a single hardened Alpine-based image
- **Production-Ready Package**: Installable via pip/pipx with proper dependency management
- **Rich Terminal Output**: Beautiful, color-coded tables and progress indicators using the Rich library
- **Multi-Scanner Support**: Works with both Grype and Trivy scanners
- **SBOM Auto-Scan**: Automatically detects and scans Syft SBOM files with Grype
- **Auto-Conversion**: Automatically converts Grype reports to CycloneDX format for Trivy scanning
- **CVE Deduplication**: Combines identical vulnerabilities across multiple scans
- **Automatic Null CVSS Filtering**: Filters out invalid CVSS scores (null, N/A, or zero) from all vulnerability reports
- **CVSS 3.x-Based Severity Selection**: Optional mode to select highest severity based on actual CVSS 3.x base scores
- **Scanner Source Tracking**: Identifies which scanner (Grype or Trivy) provided the vulnerability data
- **Occurrence Tracking**: Counts how many times each CVE appears
- **Flexible CLI**: Click-based interface with rich-click styling and sensible defaults
- **Full Test Coverage**: Comprehensive test suite with pytest
- **Security Hardened**: Non-root user (UID 1001), minimal Alpine base, pinned dependencies, and vulnerability-scanned

## Quick Start

=== "Docker (Recommended)"

    ```bash
    # Build the image
    docker build -t cve-report-aggregator .

    # Run with mounted volumes
    docker run --rm \
      -v $(pwd)/reports:/workspace/reports:ro \
      cve-report-aggregator \
      --input-dir /workspace/reports \
      --output-file /workspace/output/unified-report.json \
      --verbose
    ```

=== "pip/pipx"

    ```bash
    # Install globally
    pip install cve-report-aggregator

    # Or install with pipx (recommended)
    pipx install cve-report-aggregator

    # Run
    cve-report-aggregator --help
    ```

=== "From Source"

    ```bash
    # Clone and install
    git clone https://github.com/mkm29/cve-report-aggregator.git
    cd cve-report-aggregator
    pip install -e ".[dev]"

    # Run
    cve-report-aggregator --help
    ```

## Next Steps

- [Installation Guide](getting-started/installation.md) - Detailed installation instructions
- [Quick Start Guide](getting-started/quickstart.md) - Get up and running quickly
- [Configuration](configuration/overview.md) - Configure the aggregator
- [CLI Reference](user-guide/cli.md) - Full command-line reference

## Project Structure

```
cve-report-aggregator/
├── src/
│   └── cve_report_aggregator/
│       ├── __init__.py           # Package exports and metadata
│       ├── cli.py                # CLI entry point
│       ├── config.py             # Configuration management
│       ├── models.py             # Type definitions
│       ├── utils.py              # Utility functions
│       ├── severity.py           # CVSS and severity logic
│       ├── scanner.py            # Scanner integrations
│       ├── aggregator.py         # Deduplication engine
│       └── report.py             # Report generation
├── tests/                        # Test suite
├── docs/                         # Documentation
├── docker/                       # Docker configuration
├── pyproject.toml                # Project configuration
├── README.md                     # Project README
└── LICENSE                       # MIT License
```

## License

MIT License - See [LICENSE](https://github.com/mkm29/cve-report-aggregator/blob/main/LICENSE) file for details.

## Contributing

Contributions are welcome! Please see the [Contributing Guide](development/contributing.md) for details.
