# Configuration Guide

CVE Report Aggregator supports multiple configuration sources with a clear priority order, allowing flexible deployment in different environments.

## Configuration Priority

The application merges configuration from multiple sources with the following priority (from highest to lowest):

1. **CLI Arguments** - Command-line flags override all other sources
2. **YAML Configuration File** - Explicit config file via `--config` flag
3. **Environment Variables** - Prefixed with `CVE_AGGREGATOR_`
4. **Default Values** - Built-in defaults

## Configuration Sources

### 1. CLI Arguments (Highest Priority)

All configuration options can be specified via command-line flags:

```bash
cve-report-aggregator \
  --input-dir ./reports \
  --output-file ./output.json \
  --scanner grype \
  --mode highest-score \
  --verbose
```

**Available Flags:**

| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `--config` | `-c` | Path | None | Path to YAML configuration file |
| `--input-dir` | `-i` | Path | `./reports` | Input directory containing scan reports |
| `--output-file` | `-o` | Path | `./unified-report.json` | Output file path |
| `--scanner` | `-s` | Choice | `grype` | Scanner type: `grype` or `trivy` |
| `--mode` | `-m` | Choice | `highest-score` | Aggregation mode (see below) |
| `--verbose` | `-v` | Flag | `false` | Enable verbose output |

**Aggregation Modes:**

- `highest-score` - Select highest CVSS 3.x score across all reports
- `first-occurrence` - Use severity from first occurrence (fastest)
- `grype-only` - Process only with Grype scanner
- `trivy-only` - Process only with Trivy scanner

### 2. YAML Configuration File

YAML files provide a convenient way to maintain consistent configurations across runs.

#### Auto-Discovery

The application automatically searches for configuration files in these locations:

1. `./cve-aggregator.yaml` (current directory)
2. `./cve-aggregator.yml` (current directory)
3. `~/.config/cve-aggregator/config.yaml` (user config)
4. `~/.config/cve-aggregator/config.yml` (user config)

#### Explicit Configuration

Specify a custom configuration file:

```bash
cve-report-aggregator --config /path/to/custom-config.yaml
```

#### YAML Structure

```yaml
# Input directory containing scan report files
input_dir: ./reports

# Output file path for the unified report
output_file: ./unified-report.json

# Scanner type: grype or trivy
scanner: grype

# Aggregation mode
mode: highest-score

# Enable verbose output
verbose: false
```

#### Example Configurations

**Example 1: Trivy Scanner with Highest Scores**

```yaml
# config-trivy.yaml
scanner: trivy
mode: highest-score
verbose: true
input_dir: /var/scans/reports
output_file: /var/scans/unified-report.json
```

Usage:

```bash
cve-report-aggregator --config config-trivy.yaml
```

**Example 2: Grype-Only Mode**

```yaml
# config-grype-only.yaml
mode: grype-only
input_dir: ./grype-scans
output_file: ./grype-unified.json
verbose: false
```

**Example 3: First-Occurrence Mode (Fast)**

```yaml
# config-fast.yaml
mode: first-occurrence
scanner: grype
verbose: false
```

### 3. Environment Variables

All configuration options can be set via environment variables with the `CVE_AGGREGATOR_` prefix.

#### Variable Names

Environment variables use uppercase with underscores:

```bash
export CVE_AGGREGATOR_INPUT_DIR=/path/to/reports
export CVE_AGGREGATOR_OUTPUT_FILE=/path/to/output.json
export CVE_AGGREGATOR_SCANNER=trivy
export CVE_AGGREGATOR_MODE=highest-score
export CVE_AGGREGATOR_VERBOSE=true
```

#### Usage in Docker/Kubernetes

Environment variables are particularly useful for containerized deployments:

```dockerfile
# Dockerfile
ENV CVE_AGGREGATOR_INPUT_DIR=/app/reports
ENV CVE_AGGREGATOR_OUTPUT_FILE=/app/output/unified-report.json
ENV CVE_AGGREGATOR_SCANNER=grype
ENV CVE_AGGREGATOR_MODE=highest-score
```

```yaml
# kubernetes-deployment.yaml
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: cve-aggregator
    image: cve-report-aggregator:latest
    env:
    - name: CVE_AGGREGATOR_INPUT_DIR
      value: /mnt/reports
    - name: CVE_AGGREGATOR_OUTPUT_FILE
      value: /mnt/output/report.json
    - name: CVE_AGGREGATOR_SCANNER
      value: trivy
    - name: CVE_AGGREGATOR_MODE
      value: highest-score
    - name: CVE_AGGREGATOR_VERBOSE
      value: "true"
```

#### .env File Support

The application also supports `.env` files in the current directory:

```bash
# .env
CVE_AGGREGATOR_INPUT_DIR=./reports
CVE_AGGREGATOR_OUTPUT_FILE=./unified.json
CVE_AGGREGATOR_SCANNER=grype
CVE_AGGREGATOR_MODE=highest-score
CVE_AGGREGATOR_VERBOSE=false
```

### 4. Default Values (Lowest Priority)

If no configuration is provided, these defaults are used:

```python
input_dir: ./reports
output_file: ./unified-report.json
scanner: grype
mode: highest-score
verbose: false
```

## Configuration Merging

### Priority Example

Given the following configuration sources:

**YAML File (`config.yaml`):**

```yaml
scanner: trivy
mode: trivy-only
verbose: false
```

**Environment Variables:**

```bash
export CVE_AGGREGATOR_MODE=highest-score
```

**CLI Arguments:**

```bash
cve-report-aggregator --config config.yaml --verbose
```

**Resulting Configuration:**

```
scanner: trivy              # from YAML
mode: highest-score         # from environment (overrides YAML)
verbose: true               # from CLI (overrides YAML)
input_dir: ./reports        # from defaults
output_file: ./unified-report.json  # from defaults
```

### None Values Don't Override

CLI arguments with `None` values (not specified) don't override other sources:

```bash
# This will NOT override scanner from YAML/env
cve-report-aggregator --config config.yaml
```

Only explicitly provided CLI arguments override other sources.

## Validation

All configuration values are validated using Pydantic:

### Path Validation

- `input_dir` must exist and be a directory
- `output_file` parent directory must exist
- `config_file` must exist and be a file

### Type Validation

- `scanner` must be either `grype` or `trivy`
- `mode` must be one of: `highest-score`, `first-occurrence`, `grype-only`, `trivy-only`
- `verbose` must be a boolean

### Validation Errors

Clear error messages are displayed for invalid configurations:

```bash
$ cve-report-aggregator --input-dir /nonexistent
Error: Configuration validation failed:
  input_dir: Input directory does not exist: /nonexistent
```

## Creating Example Configuration

Copy the provided example:

```bash
cp cve-aggregator.example.yaml cve-aggregator.yaml
# Edit cve-aggregator.yaml as needed
```

## Best Practices

### 1. Use YAML for Team Environments

Store team configuration in version control:

```bash
# .gitignore
cve-aggregator.local.yaml

# Team config in repo
cve-aggregator.yaml
```

### 2. Environment Variables for CI/CD

Use environment variables in automated pipelines:

```yaml
# .github/workflows/scan.yml
- name: Aggregate CVE Reports
  env:
    CVE_AGGREGATOR_INPUT_DIR: ${{ github.workspace }}/reports
    CVE_AGGREGATOR_OUTPUT_FILE: ${{ github.workspace }}/unified.json
    CVE_AGGREGATOR_MODE: highest-score
  run: cve-report-aggregator
```

### 3. CLI Overrides for Development

Use YAML for base config, CLI for quick overrides:

```bash
# Use team config but enable verbose for debugging
cve-report-aggregator --config team-config.yaml --verbose
```

### 4. Separate Configs for Different Scanners

Maintain separate configurations for different scanner workflows:

```bash
# Grype workflow
cve-report-aggregator --config grype-config.yaml

# Trivy workflow
cve-report-aggregator --config trivy-config.yaml
```

## Troubleshooting

### Config Not Loading

Check the search paths:

```bash
# Current directory
ls -la cve-aggregator.yaml

# User config directory
ls -la ~/.config/cve-aggregator/config.yaml
```

### Validation Errors

Run with explicit config to see validation errors:

```bash
cve-report-aggregator --config config.yaml --verbose
```

### Priority Issues

Use verbose mode to see which config sources are active:

```bash
cve-report-aggregator --verbose
# Shows: "Config file: /path/to/config.yaml"
```

### Environment Variable Not Working

Verify environment variables are exported:

```bash
env | grep CVE_AGGREGATOR
```

## Advanced Usage

### Programmatic Configuration

Use the config module in Python scripts:

```python
from pathlib import Path
from cve_report_aggregator.config import get_config

# Load from YAML
config = get_config(config_file_path=Path("./config.yaml"))

# Override with CLI args
config = get_config(
    cli_args={"verbose": True, "mode": "highest-score"},
    config_file_path=Path("./config.yaml")
)

print(f"Scanner: {config.scanner}")
print(f"Mode: {config.mode}")
```

### Custom Validation

Extend the configuration model:

```python
from cve_report_aggregator.models import AggregatorConfig

# Use custom validation
config = AggregatorConfig(
    input_dir=Path("./reports"),
    output_file=Path("./output.json"),
    scanner="grype",
    mode="highest-score",
    verbose=True
)
```

## See Also

- [README.md](https://github.com/mkm29/cve-report-aggregator/blob/main/README.md) - General usage documentation
- [CLAUDE.md](https://github.com/mkm29/cve-report-aggregator/blob/main/CLAUDE.md) - Project architecture and patterns
- [API Reference](../reference/api.md) - Programmatic API documentation
