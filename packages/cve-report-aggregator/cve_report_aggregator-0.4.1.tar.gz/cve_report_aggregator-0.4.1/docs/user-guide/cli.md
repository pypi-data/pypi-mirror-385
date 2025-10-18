# CLI Reference

Complete command-line interface reference for CVE Report Aggregator.

## Command Syntax

```bash
cve-report-aggregator [OPTIONS]
```

## Options

### Input/Output

| Option          | Short | Type   | Description                                      | Default                 |
| --------------- | ----- | ------ | ------------------------------------------------ | ----------------------- |
| `--input-dir`   | `-i`  | Path   | Input directory containing scan reports or SBOMs | `./reports`             |
| `--output-file` | `-o`  | Path   | Output file path for unified report              | `./unified-report.json` |
| `--config`      | `-c`  | Path   | Path to YAML configuration file                  | Auto-discovered         |

### Scanner Configuration

| Option      | Short | Type                                                | Description                          | Default          |
| ----------- | ----- | --------------------------------------------------- | ------------------------------------ | ---------------- |
| `--scanner` | `-s`  | `grype` \| `trivy`                                  | Scanner type to process              | `grype`          |
| `--mode`    | `-m`  | `highest-score` \| `first-occurrence` \| `*-only`   | Aggregation mode                     | `highest-score`  |

**Mode Options:**
- `highest-score`: Select highest CVSS 3.x score across all reports
- `first-occurrence`: Use severity from first occurrence
- `grype-only`: Process only with Grype scanner
- `trivy-only`: Process only with Trivy scanner

### Output Options

| Option      | Short | Type    | Description                                 | Default |
| ----------- | ----- | ------- | ------------------------------------------- | ------- |
| `--verbose` | `-v`  | Boolean | Enable verbose output with detailed processing | `false` |

### Information Options

| Option      | Short | Description            |
| ----------- | ----- | ---------------------- |
| `--help`    | `-h`  | Show help message      |
| `--version` |       | Show version and exit  |

## Examples

### Basic Usage

```bash
# Use defaults (./reports → ./unified-report.json)
cve-report-aggregator

# Specify custom paths
cve-report-aggregator -i /path/to/reports -o /path/to/output.json

# Enable verbose output
cve-report-aggregator -v
```

### Scanner Selection

```bash
# Use Grype (default)
cve-report-aggregator --scanner grype

# Use Trivy
cve-report-aggregator --scanner trivy
```

### Aggregation Modes

```bash
# Use highest severity across all reports
cve-report-aggregator --mode highest-score

# Use first occurrence severity
cve-report-aggregator --mode first-occurrence

# Process only Grype reports
cve-report-aggregator --mode grype-only

# Process only Trivy reports
cve-report-aggregator --mode trivy-only
```

### Combined Options

```bash
cve-report-aggregator \
  --input-dir ./scans \
  --output-file ./results/unified.json \
  --scanner trivy \
  --mode highest-score \
  --verbose
```

### Using Configuration File

```bash
# Use auto-discovered .cve-aggregator.yaml
cve-report-aggregator

# Specify explicit config file
cve-report-aggregator --config /path/to/config.yaml
```

## Environment Variables

All CLI options can be set via environment variables with the `CVE_AGGREGATOR_` prefix:

```bash
export CVE_AGGREGATOR_INPUT_DIR=/path/to/reports
export CVE_AGGREGATOR_OUTPUT_FILE=/path/to/output.json
export CVE_AGGREGATOR_SCANNER=trivy
export CVE_AGGREGATOR_MODE=highest-score
export CVE_AGGREGATOR_VERBOSE=true
```

## Configuration Priority

Configuration sources are merged with the following priority (from highest to lowest):

1. **CLI Arguments** - Command-line flags override all other sources
2. **YAML Configuration File** - Explicit config file via `--config` flag
3. **Environment Variables** - Prefixed with `CVE_AGGREGATOR_`
4. **Default Values** - Built-in defaults

See the [Configuration Guide](../configuration/overview.md) for more details.

## Exit Codes

| Code | Meaning                                      |
| ---- | -------------------------------------------- |
| 0    | Success                                      |
| 1    | General error (invalid arguments, etc.)      |
| 2    | Configuration error                          |
| 3    | Input/output error (file not found, etc.)    |
| 4    | Scanner error (tool not found, scan failed)  |

## Next Steps

- [Configuration Overview](../configuration/overview.md) - Learn about configuration options
- [Output Format](output.md) - Understanding the unified report format
- [Scanners](scanners.md) - Learn about supported scanners
