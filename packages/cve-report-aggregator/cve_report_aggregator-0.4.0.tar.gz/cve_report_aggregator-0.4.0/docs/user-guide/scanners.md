# Scanner Support

CVE Report Aggregator supports both Grype and Trivy vulnerability scanners, with automatic format conversion and intelligent deduplication.

## Supported Scanners

### Grype (Default)

[Grype](https://github.com/anchore/grype) is Anchore's open-source vulnerability scanner for container images and filesystems.

**Features:**
- Fast scanning with comprehensive vulnerability database
- Supports multiple package ecosystems
- SBOM generation and scanning
- Native JSON output format

**Usage:**
```bash
# Scan with Grype (default)
cve-report-aggregator --scanner grype

# Or omit the flag (grype is default)
cve-report-aggregator
```

### Trivy

[Trivy](https://github.com/aquasecurity/trivy) is Aqua Security's comprehensive security scanner.

**Features:**
- Multi-scanner (vulnerabilities, misconfigurations, secrets)
- CycloneDX SBOM support
- Extensive vulnerability database
- Cloud-native focus

**Usage:**
```bash
# Scan with Trivy
cve-report-aggregator --scanner trivy
```

## Format Conversion

The aggregator automatically handles format conversion between scanners:

### Grype to CycloneDX (for Trivy)

When using Trivy scanner with Grype reports:

1. Grype JSON reports are converted to CycloneDX format using Syft
2. Trivy scans the CycloneDX SBOM
3. Results are aggregated and deduplicated

```bash
# Scan with Grype, aggregate with Trivy
grype myapp:latest -o json > reports/app.json
cve-report-aggregator --scanner trivy -i reports/
```

### SBOM Detection

The tool automatically detects Syft SBOM files and scans them with Grype:

```bash
# Generate SBOM with Syft
syft myapp:latest -o json > sboms/app.json

# Auto-detect and scan SBOM
cve-report-aggregator -i sboms/
```

## Scanner-Specific Behavior

### Grype Workflow

1. Load JSON reports directly from `matches[]` field
2. Automatically detect Syft SBOM files (has `artifacts` + `descriptor` fields)
3. Scan detected SBOMs with Grype: `grype sbom:<file> -o json`
4. Extract image name from `source.target.userInput`

### Trivy Workflow

1. Convert Grype reports to CycloneDX format using Syft
2. Scan CycloneDX SBOM with Trivy: `trivy sbom <file> -f json`
3. Normalize Trivy data to Grype-like structure for consistency
4. Extract image name from `ArtifactName`

## Multi-Scanner Workflows

### Combining Grype and Trivy

Scan the same images with both scanners and aggregate results:

```bash
# Scan with Grype
grype myapp:latest -o json > reports/grype-app.json

# Scan with Trivy
trivy image myapp:latest -f json -o reports/trivy-app.json

# Aggregate with highest severity mode
cve-report-aggregator --mode highest-score -i reports/
```

This produces a unified report with:
- All unique CVEs from both scanners
- Highest severity selected based on CVSS 3.x scores
- Source tracking showing which scanner found each CVE

### Scanner-Only Modes

Process reports from only one scanner type:

```bash
# Process only Grype reports
cve-report-aggregator --mode grype-only

# Process only Trivy reports
cve-report-aggregator --mode trivy-only
```

## Scanner Prerequisites

### Grype Requirements

```bash
# Install Grype
brew install grype

# Verify installation
grype version
```

### Trivy Requirements

```bash
# Install Syft (for format conversion)
brew install syft

# Install Trivy
brew install aquasecurity/trivy/trivy

# Verify installations
syft version
trivy version
```

## Next Steps

- [Deduplication Logic](deduplication.md) - Learn how CVEs are deduplicated
- [Output Format](output.md) - Understanding the unified report
- [CLI Reference](cli.md) - Full command-line reference
