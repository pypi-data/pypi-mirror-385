# CVE Report Aggregation and Deduplication Tool

[![Python Version](https://img.shields.io/badge/python-3.12%20%7C%203.13-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/cve-report-aggregator.svg)](https://pypi.org/project/cve-report-aggregator/)
[![PyPI downloads](https://img.shields.io/pypi/dm/cve-report-aggregator.svg)](https://pypi.org/project/cve-report-aggregator/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![CI](https://github.com/mkm29/cve-report-aggregator/actions/workflows/test.yml/badge.svg)](https://github.com/mkm29/cve-report-aggregator/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/mkm29/cve-report-aggregator/branch/main/graph/badge.svg?token=mJcMNSlBIM)](https://codecov.io/gh/mkm29/cve-report-aggregator)
[![Latest Release](https://img.shields.io/github/v/release/mkm29/cve-report-aggregator)](https://github.com/mkm29/cve-report-aggregator/releases)
[![Docker](https://img.shields.io/badge/docker-available-blue.svg)](https://github.com/mkm29/cve-report-aggregator/pkgs/container/cve-report-aggregator)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

![CVE Report Aggregator Logo](./images/logo.png)

A Python package for aggregating and deduplicating Grype and Trivy vulnerability scan reports.

## Features

- **Self-Contained Docker Image**: Includes all scanning tools (Grype, Syft, Trivy, UDS CLI) in a single hardened
  Alpine-based image
- **Supply Chain Security**: SLSA Level 3 compliant with signed images, SBOMs, and provenance attestations
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
- **Parallel Processing**: Concurrent package downloading with configurable worker pools (10-14x speedup)
- **Flexible CLI**: Click-based interface with rich-click styling and sensible defaults
- **Full Test Coverage**: Comprehensive test suite with pytest (237 tests, 91% coverage)
- **Security Hardened**: Non-root user (UID 1001), minimal Alpine base, pinned dependencies, and vulnerability-scanned

## Performance

CVE Report Aggregator now supports **parallel processing** for significantly faster execution with large package sets:

### Parallel Package Downloading

When downloading SBOM reports from remote registries (e.g., using UDS Zarf), packages are downloaded concurrently using
a configurable worker pool:

```yaml
# .cve-aggregator.yaml
maxWorkers: 14  # Number of concurrent download workers (optional)
```

**Performance Improvement:**

- **Before**: Sequential downloads (~150 seconds for 14 packages)
- **After**: Parallel downloads (~10-15 seconds for 14 packages)
- **Speedup**: **10-14x faster** for the download phase

**Auto-Detection:** If `maxWorkers` is not specified, the optimal worker count is automatically detected using the
formula: `min(32, cpu_count + 4)`. Set to `1` to disable parallelization.

**Thread Safety:** All parallel operations use thread-safe data structures (`Lock()`) to ensure data integrity across
concurrent workers.

For detailed information about the optimization plan and future phases (parallel SBOM scanning and report processing),
see [PERFORMANCE_OPTIMIZATION.md](PERFORMANCE_OPTIMIZATION.md).

## Prerequisites

**Optional (depending on scanner choice):**

- [grype](https://github.com/anchore/grype) - For Grype scanning (default scanner)
- [syft](https://github.com/anchore/syft) - For converting reports to CycloneDX format (Trivy workflow)
- [trivy](https://github.com/aquasecurity/trivy) - For Trivy scanning

```bash
# Install Grype
brew install grype

# Install syft (for Trivy workflow)
brew install syft

# Install trivy
brew install aquasecurity/trivy/trivy
```

## Installation

### Using Docker (Recommended)

The easiest way to use CVE Report Aggregator is via the pre-built Docker image, which includes all necessary scanning
tools (Grype, Syft, Trivy, UDS CLI):

```bash
# Pull the latest signed image from GitHub Container Registry
docker pull ghcr.io/mkm29/cve-report-aggregator:latest

# Or build locally
docker build -t cve-report-aggregator .

# Or use Docker Compose
docker compose run cve-aggregator --help

# Run with mounted volumes for reports and output
docker run --rm \
  -v $(pwd)/reports:/workspace/reports:ro \
  -v $(pwd)/output:/home/cve-aggregator/output \
  ghcr.io/mkm29/cve-report-aggregator:latest \
  --input-dir /workspace/reports \
  --verbose

# Note: Output files are automatically saved to $HOME/output with timestamped names
# Format: <package_name>-YYYYMMDDhhmmss.json (e.g., gitlab-20251019182051.json)
```

#### Image Security & Supply Chain

All container images are built with enterprise-grade security:

- **Signed with Cosign**: Keyless signing using GitHub OIDC identity
- **SBOM Included**: CycloneDX and SPDX attestations attached to every image
- **Provenance**: SLSA Level 3 compliant build attestations
- **Multi-Architecture**: Supports both amd64 and arm64 (Apple Silicon)
- **Vulnerability Scanned**: Regularly scanned with Grype and Trivy

##### Verify Image Signature

```bash
# Install cosign
brew install cosign

# Verify the image signature
cosign verify ghcr.io/mkm29/cve-report-aggregator:latest \
  --certificate-identity-regexp='https://github.com/mkm29/cve-report-aggregator' \
  --certificate-oidc-issuer='https://token.actions.githubusercontent.com'

# Output shows verified signature with GitHub Actions identity
```

##### Download and Verify SBOM

```bash
# Download CycloneDX SBOM (JSON format)
cosign verify-attestation ghcr.io/mkm29/cve-report-aggregator:latest \
  --type cyclonedx \
  --certificate-identity-regexp='https://github.com/mkm29/cve-report-aggregator' \
  --certificate-oidc-issuer='https://token.actions.githubusercontent.com' | \
  jq -r '.payload' | base64 -d | jq . > sbom-cyclonedx.json

# Download SPDX SBOM (JSON format)
cosign verify-attestation ghcr.io/mkm29/cve-report-aggregator:latest \
  --type spdx \
  --certificate-identity-regexp='https://github.com/mkm29/cve-report-aggregator' \
  --certificate-oidc-issuer='https://token.actions.githubusercontent.com' | \
  jq -r '.payload' | base64 -d | jq . > sbom-spdx.json

# View all attestations and signatures
cosign tree ghcr.io/mkm29/cve-report-aggregator:latest
```

##### Download Build Provenance

```bash
# Download SLSA provenance attestation
cosign verify-attestation ghcr.io/mkm29/cve-report-aggregator:latest \
  --type slsaprovenance \
  --certificate-identity-regexp='https://github.com/mkm29/cve-report-aggregator' \
  --certificate-oidc-issuer='https://token.actions.githubusercontent.com' | \
  jq -r '.payload' | base64 -d | jq . > provenance.json
```

#### Available Image Tags

Images are published to GitHub Container Registry with the following tags:

- `latest` - Latest stable release (recommended for production)
- `v*.*.*` - Specific version tags (e.g., `v0.5.1`, `v0.5.2`)
- `rc` - Release candidate builds (for testing pre-release versions)

```bash
# Pull specific version
docker pull ghcr.io/mkm29/cve-report-aggregator:v0.5.1

# Pull latest stable
docker pull ghcr.io/mkm29/cve-report-aggregator:latest

# Pull release candidate (if available)
docker pull ghcr.io/mkm29/cve-report-aggregator:rc
```

All tags are signed and include full attestations (signature, SBOM, provenance).

## Docker Credentials Management

The Docker container supports two methods for providing registry credentials:

1. **Build-Time Secrets**
1. **Environment Variables**

### Method 1: Build-Time Secrets (Recommended)

**Best for**: Private container images where credentials can be baked in securely.

Create a credentials file in JSON format with `username`, `password`, and `registry` fields:

```bash
cat > docker/config.json <<EOF
{
  "username": "myuser",
  "password": "mypassword",
  "registry": "ghcr.io"
}
EOF
chmod 600 docker/config.json
```

**Important**: Always encrypt the credentials file with SOPS before committing:

```bash
# Encrypt the credentials file
sops -e docker/config.json.dec > docker/config.json.enc

# Or encrypt in place
sops -e docker/config.json.dec > docker/config.json.enc
```

Build the image with the secret:

```bash
# If using encrypted file, decrypt first
sops -d docker/config.json.enc > docker/config.json.dec

# Build with the decrypted credentials
docker buildx build \
  --secret id=credentials,src=./docker/config.json.dec \
  -f docker/Dockerfile \
  -t cve-report-aggregator:latest .

# Remove decrypted file after build
rm docker/config.json.dec
```

Or build directly with unencrypted file (for local development):

```bash
docker buildx build \
  --secret id=credentials,src=./docker/config.json \
  -f docker/Dockerfile \
  -t cve-report-aggregator:latest .
```

The credentials will be stored in the image at `$DOCKER_CONFIG/config.json` (defaults to
`/home/cve-aggregator/.docker/config.json`) in proper Docker authentication format with base64-encoded credentials.

Run the container (no runtime credentials needed - uses baked-in config.json):

```bash
docker run --rm cve-report-aggregator:latest --help
```

**Important**: This method bakes credentials into the image. Only use for private registries and **never** push images
with credentials to public registries.

### Method 2: Environment Variables (Development Only)

**Warning**: This method exposes the password in process listings and Docker inspect output. Only use for
development/testing.

```bash
docker run -it --rm \
  -e REGISTRY_URL="$UDS_URL" \
  -e UDS_USERNAME="$UDS_USERNAME" \
  -e UDS_PASSWORD="$UDS_PASSWORD" \
  cve-report-aggregator:latest --help
```

### How Credentials Are Handled

The `entrypoint.sh` script checks for Docker authentication on startup:

1. **Docker config.json** (Build-Time): Checks if `$DOCKER_CONFIG/config.json` exists

   - If found: Skips all credential checks and login - uses existing Docker auth
   - Location: `/home/cve-aggregator/.docker/config.json`

1. **Environment Variables** (if config.json not found): Requires all three variables:

   - `REGISTRY_URL` - Registry URL (e.g., `registry.defenseunicorns.com`)
   - `UDS_USERNAME` - Registry username
   - `UDS_PASSWORD` - Registry password

If config.json doesn't exist and environment variables are not provided, the container exits with an error.

**Important**: Mounting your local `~/.docker/config.json` file into the container will **not** work. The Docker config
must be baked into the image during build (Method 1) or you must use environment variables (Method 2). UDS/Zarf requires
credentials in a specific format that differs from standard Docker auth.

### From Source

```bash
# Clone the repository
git clone https://github.com/mkm29/cve-report-aggregator.git
cd cve-report-aggregator

# Install in development mode
pip install -e .

# Or install with dev dependencies
pip install -e ".[dev]"
```

### From PyPI (when published)

```bash
# Install globally
pip install cve-report-aggregator

# Or install with pipx (recommended)
pipx install cve-report-aggregator
```

## Usage

### Basic Usage (Default Locations)

Process reports from `./reports/` and automatically save timestamped output to `$HOME/output/`:

```bash
cve-report-aggregator
# Output: $HOME/output/unified-YYYYMMDDhhmmss.json
```

### Use Trivy Scanner

Automatically convert reports to CycloneDX and scan with Trivy:

```bash
cve-report-aggregator --scanner trivy
```

### Process SBOM Files

The script automatically detects and scans Syft SBOM files:

```bash
cve-report-aggregator -i /path/to/sboms -v
```

### Custom Input Directory

```bash
# Specify custom input directory (output still goes to $HOME/output with timestamp)
cve-report-aggregator -i /path/to/reports
```

### Verbose Mode

Enable detailed processing output:

```bash
cve-report-aggregator -v
```

### Combined Options

```bash
cve-report-aggregator -i ./scans --scanner trivy -v
# Output: $HOME/output/<package>-YYYYMMDDhhmmss.json
```

### Use Highest Severity Across Scanners

When scanning with multiple scanners (or multiple runs of the same scanner), automatically select the highest severity
rating:

```bash
# Scan the same image with both Grype and Trivy, use highest severity
grype myapp:latest -o json > reports/grype-app.json
trivy image myapp:latest -f json -o reports/trivy-app.json
cve-report-aggregator -i reports/ --mode highest-score
# Output: $HOME/output/unified-YYYYMMDDhhmmss.json
```

This is particularly useful when:

- Combining results from multiple scanners with different severity assessments
- Ensuring conservative (worst-case) severity ratings for compliance
- Aggregating multiple scans over time where severity data may have been updated

## Command-Line Options

| Option          | Short | Description                                                                          | Default                                   |
| --------------- | ----- | ------------------------------------------------------------------------------------ | ----------------------------------------- |
| `--input-dir`   | `-i`  | Input directory containing scan reports or SBOMs                                     | `./reports`                               |
| `--output-file` | `-o`  | _(Deprecated)_ Output path reference (files saved to `$HOME/output/` with timestamp) | `$HOME/output/<package>-<timestamp>.json` |
| `--scanner`     | `-s`  | Scanner type to process (`grype` or `trivy`)                                         | `grype`                                   |
| `--log-level`   | `-l`  | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)                                | `INFO`                                    |
| `--mode`        | `-m`  | Aggregation mode: `highest-score`, `first-occurrence`, `grype-only`, `trivy-only`    | `highest-score`                           |
| `--help`        | `-h`  | Show help message and exit                                                           | N/A                                       |
| `--version`     |       | Show version and exit                                                                | N/A                                       |

**Note:** All output files are automatically saved to `$HOME/output/` with timestamped filenames in the format
`<package_name>-YYYYMMDDhhmmss.json`. When processing multiple packages, each gets its own timestamped file (e.g.,
`gitlab-20251019182051.json`, `gitlab-runner-20251019182055.json`).

### Configuration File Options

Additional options can be configured via `.cve-aggregator.yaml` or `.cve-aggregator.yml`:

| Option                   | Type    | Description                                                | Default                               |
| ------------------------ | ------- | ---------------------------------------------------------- | ------------------------------------- |
| `maxWorkers`             | integer | Maximum concurrent workers for parallel downloads          | Auto-detect: `min(32, cpu_count + 4)` |
| `registry`               | string  | Container registry URL for remote package downloads        | None                                  |
| `organization`           | string  | Organization/namespace in the registry                     | None                                  |
| `packages`               | array   | List of packages to download (name, version, architecture) | `[]`                                  |
| `downloadRemotePackages` | boolean | Enable downloading SBOM reports from remote registry       | `false`                               |

**Example Configuration:**

```yaml
# .cve-aggregator.yaml
maxWorkers: 14
registry: registry.defenseunicorns.com
organization: sld-45
downloadRemotePackages: true
packages:
  - name: gitlab
    version: 18.4.2-uds.0-unicorn
    architecture: amd64
  - name: gitlab-runner
    version: 18.4.0-uds.0-unicorn
    architecture: amd64
```

See [.cve-aggregator.example.yaml](.cve-aggregator.example.yaml) for a complete configuration example.

## Output Format

The unified report includes:

### Metadata

- Generation timestamp
- Scanner type and version
- Source report count and filenames

### Summary

- Total vulnerability occurrences
- Unique vulnerability count
- Severity breakdown (Critical, High, Medium, Low, Negligible, Unknown)
- Per-image scan results

### Vulnerabilities (Deduplicated)

For each unique CVE/GHSA:

- Vulnerability ID
- Occurrence count
- Selected scanner (which scanner provided the vulnerability data)
- Severity and CVSS scores
- Fix availability and versions
- All affected sources (images and artifacts)
- Detailed match information

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=cve_report_aggregator --cov-report=html

# Run specific test file
pytest tests/test_severity.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

### Building the Package

```bash
# Build distribution packages
python -m build

# Install locally
pip install dist/cve_report_aggregator-0.1.0-py3-none-any.whl
```

## Project Structure

```bash
cve-report-aggregator/
├── src/
│   └── cve_report_aggregator/
│       ├── __init__.py           # Package exports and metadata
│       ├── main.py               # CLI entry point
│       ├── models.py             # Type definitions
│       ├── utils.py              # Utility functions
│       ├── severity.py           # CVSS and severity logic
│       ├── scanner.py            # Scanner integrations
│       ├── aggregator.py         # Deduplication engine
│       └── report.py             # Report generation
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # Pytest fixtures
│   ├── test_severity.py          # Severity tests
│   └── test_aggregator.py        # Aggregation tests
├── pyproject.toml                # Project configuration
├── README.md                     # This file
└── LICENSE                       # MIT License
```

## Example Workflows

### Docker E2E Workflow

```bash
# Scan container images and aggregate with Docker
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v $(pwd)/reports:/workspace/reports \
  -v $(pwd)/output:/home/cve-aggregator/output \
  ghcr.io/mkm29/cve-report-aggregator:latest bash -c "\
    grype nginx:latest -o json > /workspace/reports/nginx.json && \
    grype postgres:15 -o json > /workspace/reports/postgres.json && \
    cve-report-aggregator --input-dir /workspace/reports --log-level DEBUG"

# View results (find the most recent timestamped file)
jq '.summary' output/unified-*.json | tail -1
```

### Grype Workflow (Default)

```bash
# Scan multiple container images with Grype
grype registry.io/app/service1:v1.0 -o json > reports/service1.json
grype registry.io/app/service2:v1.0 -o json > reports/service2.json
grype registry.io/app/service3:v1.0 -o json > reports/service3.json

# Aggregate all reports (output saved to $HOME/output with timestamp)
cve-report-aggregator --log-level DEBUG

# Query results with jq (use the timestamped file)
REPORT=$(ls -t $HOME/output/unified-*.json | head -1)
jq '.summary' "$REPORT"
jq '.vulnerabilities[] | select(.vulnerability.severity == "Critical")' "$REPORT"
```

### SBOM Workflow

```bash
# Generate SBOMs with Syft (or use Zarf-generated SBOMs)
syft registry.io/app/service1:v1.0 -o json > sboms/service1.json
syft registry.io/app/service2:v1.0 -o json > sboms/service2.json

# Script automatically detects and scans SBOMs with Grype
cve-report-aggregator -i ./sboms --log-level DEBUG

# Results include all vulnerabilities found (use timestamped file)
REPORT=$(ls -t $HOME/output/unified-*.json | head -1)
jq '.summary.by_severity' "$REPORT"
```

### Trivy Workflow

```bash
# Start with Grype reports (script will convert to CycloneDX)
grype registry.io/app/service1:v1.0 -o json > reports/service1.json
grype registry.io/app/service2:v1.0 -o json > reports/service2.json

# Aggregate and scan with Trivy (auto-converts to CycloneDX)
cve-report-aggregator --scanner trivy --log-level DEBUG

# Or scan SBOMs directly with Trivy
cve-report-aggregator -i ./sboms --scanner trivy --log-level DEBUG

# View most recent output
REPORT=$(ls -t $HOME/output/unified-*.json | head -1)
jq '.summary' "$REPORT"
```

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please:

1. Fork the repository
1. Create a feature branch
1. Add tests for new functionality
1. Ensure all tests pass
1. Submit a pull request

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.
