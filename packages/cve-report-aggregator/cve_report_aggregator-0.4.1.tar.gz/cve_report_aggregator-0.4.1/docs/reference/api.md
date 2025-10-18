[38;2;248;248;242m# API Reference[0m

[38;2;248;248;242mAPI documentation for CVE Report Aggregator modules.[0m

[38;2;248;248;242m## Configuration (`config.py`)[0m

[38;2;248;248;242m### `AggregatorSettings`[0m

[38;2;248;248;242mPydantic Settings class for configuration management.[0m

[38;2;248;248;242m**Attributes:**[0m
[38;2;248;248;242m- `input_dir: Path` - Input directory containing scan reports[0m
[38;2;248;248;242m- `output_file: Path` - Output file path[0m
[38;2;248;248;242m- `scanner: ScannerType` - Scanner type (grype or trivy)[0m
[38;2;248;248;242m- `mode: ModeType` - Aggregation mode[0m
[38;2;248;248;242m- `verbose: bool` - Enable verbose output[0m
[38;2;248;248;242m- `config_file: Path | None` - Configuration file path[0m
[38;2;248;248;242m- `registry: str | None` - Container registry URL[0m
[38;2;248;248;242m- `organization: str | None` - Organization/namespace[0m
[38;2;248;248;242m- `packages: list[PackageConfig]` - List of packages to scan[0m

[38;2;248;248;242m### `load_settings()`[0m

[38;2;248;248;242mLoad settings from all configuration sources.[0m

[38;2;248;248;242m**Parameters:**[0m
[38;2;248;248;242m- `cli_args: dict[str, Any] | None` - CLI arguments[0m
[38;2;248;248;242m- `config_file_path: Path | None` - Explicit config file path[0m

[38;2;248;248;242m**Returns:** `AggregatorSettings`[0m

[38;2;248;248;242m### `get_config()`[0m

[38;2;248;248;242mLoad and validate complete configuration.[0m

[38;2;248;248;242m**Parameters:**[0m
[38;2;248;248;242m- `cli_args: dict[str, Any] | None` - CLI arguments[0m
[38;2;248;248;242m- `config_file_path: Path | None` - Config file path[0m

[38;2;248;248;242m**Returns:** `AggregatorConfig`[0m

[38;2;248;248;242m## Models (`models.py`)[0m

[38;2;248;248;242m### `PackageConfig`[0m

[38;2;248;248;242mPackage configuration model.[0m

[38;2;248;248;242m**Attributes:**[0m
[38;2;248;248;242m- `name: str` - Package name[0m
[38;2;248;248;242m- `version: str` - Package version[0m
[38;2;248;248;242m- `architecture: str` - Package architecture (default: amd64)[0m

[38;2;248;248;242m### `AggregatorConfig`[0m

[38;2;248;248;242mMain configuration model with validation.[0m

[38;2;248;248;242m**Attributes:**[0m
[38;2;248;248;242m- All fields from `AggregatorSettings`[0m
[38;2;248;248;242m- Includes validators for paths, scanner tools[0m

[38;2;248;248;242m## CLI (`cli.py`)[0m

[38;2;248;248;242m### `main()`[0m

[38;2;248;248;242mMain CLI entry point using Click.[0m

[38;2;248;248;242m**Parameters:**[0m
[38;2;248;248;242m- `--input-dir / -i` - Input directory[0m
[38;2;248;248;242m- `--output-file / -o` - Output file[0m
[38;2;248;248;242m- `--scanner / -s` - Scanner type[0m
[38;2;248;248;242m- `--mode / -m` - Aggregation mode[0m
[38;2;248;248;242m- `--verbose / -v` - Verbose output[0m
[38;2;248;248;242m- `--config / -c` - Config file path[0m

[38;2;248;248;242m## Next Steps[0m

[38;2;248;248;242m- [CLI Reference](../user-guide/cli.md) - Full CLI documentation[0m
[38;2;248;248;242m- [Configuration](../configuration/overview.md) - Configuration guide[0m
