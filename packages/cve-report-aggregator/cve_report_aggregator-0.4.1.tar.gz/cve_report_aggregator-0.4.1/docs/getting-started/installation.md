# Installation

CVE Report Aggregator can be installed using several methods depending on your needs.

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

## Installation Methods

### Using Docker (Recommended)

The easiest way to use CVE Report Aggregator is via the pre-built Docker image, which includes all necessary scanning tools (Grype, Syft, Trivy, UDS CLI):

```bash
# Build the image
docker build -t cve-report-aggregator .

# Or use Docker Compose
docker compose run cve-aggregator --help

# Run with mounted volumes
docker run --rm \
  -v $(pwd)/reports:/workspace/reports:ro \
  cve-report-aggregator \
  --input-dir /workspace/reports \
  --output-file /workspace/output/unified-report.json \
  --verbose
```

See the [Docker Usage Guide](docker.md) for detailed Docker configuration options including credentials management.

### From PyPI

```bash
# Install globally
pip install cve-report-aggregator

# Or install with pipx (recommended)
pipx install cve-report-aggregator
```

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

## Verifying Installation

After installation, verify that the tool is working correctly:

```bash
# Check version
cve-report-aggregator --version

# View help
cve-report-aggregator --help
```

## Next Steps

- [Quick Start Guide](quickstart.md) - Get started with basic usage
- [Configuration](../configuration/overview.md) - Learn about configuration options
- [CLI Reference](../user-guide/cli.md) - Full command-line reference
