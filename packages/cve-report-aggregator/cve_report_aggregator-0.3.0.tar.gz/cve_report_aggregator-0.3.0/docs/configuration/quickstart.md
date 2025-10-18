# Configuration Quick Start

This guide provides a quick introduction to configuring CVE Report Aggregator using different methods.

## TL;DR

```bash
# Option 1: Use CLI flags (traditional)
cve-report-aggregator -i ./reports -o ./output.json -s grype -v

# Option 2: Use YAML config file
cve-report-aggregator --config ./config.yaml

# Option 3: Use environment variables
export CVE_AGGREGATOR_SCANNER=trivy
export CVE_AGGREGATOR_VERBOSE=true
cve-report-aggregator

# Option 4: Mix and match (CLI overrides config file)
cve-report-aggregator --config ./config.yaml --verbose
```

## Quick Configuration Methods

### 1. YAML Configuration (Recommended)

Create `cve-aggregator.yaml` in your project directory:

```yaml
scanner: grype
mode: highest-score
input_dir: ./reports
output_file: ./unified-report.json
verbose: false
```

Run:

```bash
cve-report-aggregator
```

The application will automatically find and use `cve-aggregator.yaml`.

### 2. Environment Variables (Docker/CI Friendly)

```bash
export CVE_AGGREGATOR_SCANNER=trivy
export CVE_AGGREGATOR_MODE=highest-score
export CVE_AGGREGATOR_VERBOSE=true
cve-report-aggregator
```

### 3. CLI Arguments (Maximum Flexibility)

```bash
cve-report-aggregator \
  --input-dir ./reports \
  --output-file ./output.json \
  --scanner grype \
  --mode highest-score \
  --verbose
```

## Common Scenarios

### Scenario 1: Development Environment

Use YAML for base config, override with CLI for testing:

```yaml
# dev-config.yaml
scanner: grype
mode: highest-score
input_dir: ./reports
output_file: ./dev-output.json
```

```bash
# Normal development
cve-report-aggregator --config dev-config.yaml

# Test with verbose output
cve-report-aggregator --config dev-config.yaml --verbose

# Test different scanner
cve-report-aggregator --config dev-config.yaml --scanner trivy
```

### Scenario 2: CI/CD Pipeline

Use environment variables for flexibility:

```yaml
# .github/workflows/scan.yml
steps:
  - name: Aggregate Reports
    env:
      CVE_AGGREGATOR_INPUT_DIR: ${{ github.workspace }}/reports
      CVE_AGGREGATOR_OUTPUT_FILE: ${{ github.workspace }}/unified.json
      CVE_AGGREGATOR_MODE: highest-score
    run: cve-report-aggregator
```

### Scenario 3: Docker Container

Pass configuration via environment:

```dockerfile
ENV CVE_AGGREGATOR_INPUT_DIR=/app/reports
ENV CVE_AGGREGATOR_OUTPUT_FILE=/app/output/unified.json
ENV CVE_AGGREGATOR_SCANNER=grype
CMD ["cve-report-aggregator"]
```

Or mount a config file:

```bash
docker run -v $(pwd)/config.yaml:/app/config.yaml \
  cve-aggregator --config /app/config.yaml
```

### Scenario 4: Multiple Environments

Create separate config files:

```bash
# Production
cve-report-aggregator --config prod-config.yaml

# Staging
cve-report-aggregator --config staging-config.yaml

# Development
cve-report-aggregator --config dev-config.yaml
```

## Configuration Priority

When using multiple sources, priority is:

**CLI > YAML > Environment Variables > Defaults**

Example:

```yaml
# config.yaml
scanner: grype
verbose: false
```

```bash
export CVE_AGGREGATOR_SCANNER=trivy
cve-report-aggregator --config config.yaml --verbose
```

Result:

- `scanner`: `trivy` (from environment, overrides YAML)
- `verbose`: `true` (from CLI, overrides YAML)
- Other settings from `config.yaml`

## Available Options

| Option | CLI Flag | Environment Variable | YAML Key | Default |
|--------|----------|---------------------|----------|---------|
| Config File | `--config`, `-c` | N/A | N/A | None |
| Input Directory | `--input-dir`, `-i` | `CVE_AGGREGATOR_INPUT_DIR` | `input_dir` | `./reports` |
| Output File | `--output-file`, `-o` | `CVE_AGGREGATOR_OUTPUT_FILE` | `output_file` | `./unified-report.json` |
| Scanner | `--scanner`, `-s` | `CVE_AGGREGATOR_SCANNER` | `scanner` | `grype` |
| Mode | `--mode`, `-m` | `CVE_AGGREGATOR_MODE` | `mode` | `highest-score` |
| Verbose | `--verbose`, `-v` | `CVE_AGGREGATOR_VERBOSE` | `verbose` | `false` |

## Mode Options

| Mode | Description | Use Case |
|------|-------------|----------|
| `highest-score` | Select highest CVSS 3.x score | Production (most conservative) |
| `first-occurrence` | Use first found severity | Development (fastest) |
| `grype-only` | Only use Grype scanner | Grype-specific workflow |
| `trivy-only` | Only use Trivy scanner | Trivy-specific workflow |

## Getting Started

1. **Copy the example config:**

   ```bash
   cp cve-aggregator.example.yaml cve-aggregator.yaml
   ```

2. **Edit as needed:**

   ```bash
   vim cve-aggregator.yaml
   ```

3. **Run:**

   ```bash
   cve-report-aggregator
   ```

## Troubleshooting

### Config file not found

Check search locations:

```bash
ls -la cve-aggregator.yaml
ls -la ~/.config/cve-aggregator/config.yaml
```

### Validation errors

Run with explicit config to see errors:

```bash
cve-report-aggregator --config config.yaml
```

### Which config is active?

Use verbose mode:

```bash
cve-report-aggregator --verbose
# Shows: "Config file: /path/to/config.yaml"
```

## Next Steps

- See [Configuration Overview](./overview.md) for complete documentation
- See [Implementation Details](./implementation.md) for technical details
- See example config: `cve-aggregator.example.yaml`

## Examples Repository

See the `examples/` directory for:

- Development configuration
- Production configuration
- CI/CD configuration
- Docker configuration
- Kubernetes configuration
