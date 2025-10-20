# Quick Start

This guide will help you get started with CVE Report Aggregator quickly.

## Basic Usage

### Default Locations

Process reports from `./reports/` and output to `./unified-report.json`:

```bash
cve-report-aggregator
```

### Custom Input and Output

```bash
cve-report-aggregator -i /path/to/reports -o /path/to/output.json
```

### Verbose Mode

Enable detailed processing output:

```bash
cve-report-aggregator -v
```

## Scanner Workflows

### Grype Workflow (Default)

```bash
# Scan multiple container images with Grype
grype registry.io/app/service1:v1.0 -o json > reports/service1.json
grype registry.io/app/service2:v1.0 -o json > reports/service2.json
grype registry.io/app/service3:v1.0 -o json > reports/service3.json

# Aggregate all reports
cve-report-aggregator -v

# Query results with jq
jq '.summary' unified-report.json
jq '.vulnerabilities[] | select(.vulnerability.severity == "Critical")' unified-report.json
```

### Trivy Workflow

Automatically convert reports to CycloneDX and scan with Trivy:

```bash
# Start with Grype reports (script will convert to CycloneDX)
grype registry.io/app/service1:v1.0 -o json > reports/service1.json
grype registry.io/app/service2:v1.0 -o json > reports/service2.json

# Aggregate and scan with Trivy (auto-converts to CycloneDX)
cve-report-aggregator --scanner trivy -v

# Or scan SBOMs directly with Trivy
cve-report-aggregator -i ./sboms --scanner trivy -o trivy-unified.json -v
```

### SBOM Workflow

The script automatically detects and scans Syft SBOM files:

```bash
# Generate SBOMs with Syft (or use Zarf-generated SBOMs)
syft registry.io/app/service1:v1.0 -o json > sboms/service1.json
syft registry.io/app/service2:v1.0 -o json > sboms/service2.json

# Script automatically detects and scans SBOMs with Grype
cve-report-aggregator -i ./sboms -v

# Results include all vulnerabilities found
jq '.summary.by_severity' unified-report.json
```

## Aggregation Modes

### Highest Severity Mode

When scanning with multiple scanners, automatically select the highest severity rating:

```bash
# Scan the same image with both Grype and Trivy, use highest severity
grype myapp:latest -o json > reports/grype-app.json
trivy image myapp:latest -f json -o reports/trivy-app.json
cve-report-aggregator -i reports/ --mode highest-score -o unified.json
```

This is particularly useful when:

- Combining results from multiple scanners with different severity assessments
- Ensuring conservative (worst-case) severity ratings for compliance
- Aggregating multiple scans over time where severity data may have been updated

### First Occurrence Mode

Use severity from the first occurrence of each vulnerability:

```bash
cve-report-aggregator --mode first-occurrence
```

## Combined Options

```bash
cve-report-aggregator \
  -i ./scans \
  -o ./results/unified.json \
  --scanner trivy \
  --mode highest-score \
  -v
```

## Next Steps

- [Configuration Guide](../configuration/overview.md) - Learn about all configuration options
- [CLI Reference](../user-guide/cli.md) - Full command-line reference
- [Output Format](../user-guide/output.md) - Understanding the output report
