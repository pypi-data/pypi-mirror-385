# Configuration Management - Usage Examples

Quick reference guide for using the global configuration system in CVE Report Aggregator.

## Table of Contents

- [Application Startup](#application-startup)
- [Accessing Config in Modules](#accessing-config-in-modules)
- [Testing Patterns](#testing-patterns)
- [Advanced Patterns](#advanced-patterns)

## Application Startup

### Basic Setup (cli.py)

```python
from cve_report_aggregator.config import get_config, set_config

def main(input_dir, output_file, scanner, verbose, mode):
    """CLI entry point."""
    # 1. Build CLI arguments dictionary
    cli_args = {
        'input_dir': input_dir,
        'output_file': output_file,
        'scanner': scanner,
        'verbose': verbose,
        'mode': mode,
    }

    # 2. Load and validate configuration from all sources
    #    Priority: CLI args > YAML file > env vars > defaults
    app_config = get_config(cli_args=cli_args)

    # 3. Initialize global configuration for sharing across modules
    set_config(app_config)

    # 4. Rest of application logic
    # All modules can now access config via get_current_config()
```

### With YAML Configuration File

```python
from pathlib import Path
from cve_report_aggregator.config import get_config, set_config

def main(config_file, **cli_args):
    """CLI entry point with config file support."""
    # Load with explicit config file (overrides auto-discovery)
    app_config = get_config(
        cli_args=cli_args,
        config_file_path=Path(config_file) if config_file else None
    )

    # Initialize global config
    set_config(app_config)
```

### With Error Handling

```python
from pydantic import ValidationError
from cve_report_aggregator.config import get_config, set_config

def main(**cli_args):
    """CLI entry point with robust error handling."""
    try:
        # Load and validate configuration
        app_config = get_config(cli_args=cli_args)
        set_config(app_config)

    except ValidationError as e:
        print("Configuration validation failed:")
        for error in e.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            print(f"  {field}: {error['msg']}")
        sys.exit(1)

    except (FileNotFoundError, ValueError) as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
```

## Accessing Config in Modules

### Simple Access

```python
from cve_report_aggregator.config import get_current_config

def process_reports():
    """Process reports using global configuration."""
    config = get_current_config()

    if config.verbose:
        print(f"Processing reports from: {config.input_dir}")

    # Use config values
    scanner = config.scanner
    mode = config.mode
    # ...
```

### Defensive Access (Check Initialization)

```python
from cve_report_aggregator.config import is_config_initialized, get_current_config

def optional_config_access():
    """Access config with fallback behavior."""
    if is_config_initialized():
        config = get_current_config()
        verbose = config.verbose
    else:
        # Fallback behavior when config not initialized
        verbose = False

    if verbose:
        print("Verbose mode enabled")
```

### With Error Handling

```python
from cve_report_aggregator.config import get_current_config, ConfigurationError

def safe_config_access():
    """Access config with error handling."""
    try:
        config = get_current_config()
        return config.verbose
    except ConfigurationError as e:
        print(f"Warning: {e}")
        return False  # Fallback value
```

### Executor Pattern (Mixed Approach)

```python
from pathlib import Path
from cve_report_aggregator.config import get_current_config, is_config_initialized

def execute_command(command: list[str], config=None):
    """Execute command with optional config override.

    Supports both explicit config passing and global config access.
    """
    # Use explicit config if provided, otherwise try global config
    if config is None and is_config_initialized():
        try:
            config = get_current_config()
        except Exception as e:
            print(f"Warning: Failed to get config: {e}")

    # Use config if available
    cwd = config.input_dir.parent if config else None
    verbose = config.verbose if config else False

    # Execute command with context
    # ...
```

## Testing Patterns

### Basic Test with Context Manager

```python
from pathlib import Path
import pytest
from cve_report_aggregator.config import config_context
from cve_report_aggregator.models import AggregatorConfig

def test_my_feature(tmp_path):
    """Test feature with temporary configuration."""
    # Create test config
    (tmp_path / "reports").mkdir()
    test_config = AggregatorConfig(
        input_dir=tmp_path / "reports",
        output_file=tmp_path / "output.json",
        verbose=True,
        scanner="grype"
    )

    # Use context manager for isolated test
    with config_context(test_config):
        # Test code that accesses global config
        from cve_report_aggregator.config import get_current_config
        assert get_current_config().verbose is True

    # Config is automatically cleaned up after test
```

### Test Fixture for Config Reset

```python
import pytest
from cve_report_aggregator.config import reset_config

@pytest.fixture(autouse=True)
def reset_global_config():
    """Ensure clean config state before each test."""
    reset_config()  # Clean state before test
    yield
    reset_config()  # Clean state after test
```

### Testing Multiple Configurations

```python
from cve_report_aggregator.config import config_context
from cve_report_aggregator.models import AggregatorConfig

@pytest.mark.parametrize("scanner,mode", [
    ("grype", "highest-score"),
    ("trivy", "first-occurrence"),
    ("grype", "grype-only"),
])
def test_with_different_configs(tmp_path, scanner, mode):
    """Test with different configuration combinations."""
    (tmp_path / "reports").mkdir()
    test_config = AggregatorConfig(
        input_dir=tmp_path / "reports",
        output_file=tmp_path / "output.json",
        scanner=scanner,
        mode=mode
    )

    with config_context(test_config):
        from cve_report_aggregator.config import get_current_config
        config = get_current_config()
        assert config.scanner == scanner
        assert config.mode == mode
```

### Testing with Explicit Config (No Global State)

```python
from cve_report_aggregator.models import AggregatorConfig
from cve_report_aggregator.executor import execute_command

def test_executor_explicit_config(tmp_path):
    """Test executor with explicitly passed config."""
    (tmp_path / "reports").mkdir()
    test_config = AggregatorConfig(
        input_dir=tmp_path / "reports",
        output_file=tmp_path / "output.json",
        verbose=True
    )

    # Pass config explicitly (no global state needed)
    output, error = execute_command(
        ["echo", "test"],
        config=test_config
    )

    assert error is None
    assert "test" in output
```

## Advanced Patterns

### Nested Context Managers

```python
from cve_report_aggregator.config import config_context
from cve_report_aggregator.models import AggregatorConfig

def test_nested_contexts(tmp_path):
    """Test with nested configuration contexts."""
    (tmp_path / "reports1").mkdir()
    (tmp_path / "reports2").mkdir()

    config1 = AggregatorConfig(
        input_dir=tmp_path / "reports1",
        output_file=tmp_path / "output1.json",
        scanner="grype"
    )
    config2 = AggregatorConfig(
        input_dir=tmp_path / "reports2",
        output_file=tmp_path / "output2.json",
        scanner="trivy"
    )

    with config_context(config1):
        assert get_current_config().scanner == "grype"

        with config_context(config2):
            assert get_current_config().scanner == "trivy"

        # Back to config1
        assert get_current_config().scanner == "grype"

    # No config after contexts
```

### Configuration Builder Pattern

```python
from pathlib import Path
from cve_report_aggregator.models import AggregatorConfig

class ConfigBuilder:
    """Builder for test configurations."""

    def __init__(self, tmp_path: Path):
        self.tmp_path = tmp_path
        self._input_dir = None
        self._output_file = None
        self._verbose = False
        self._scanner = "grype"

    def with_verbose(self) -> 'ConfigBuilder':
        """Enable verbose mode."""
        self._verbose = True
        return self

    def with_scanner(self, scanner: str) -> 'ConfigBuilder':
        """Set scanner type."""
        self._scanner = scanner
        return self

    def build(self) -> AggregatorConfig:
        """Build configuration."""
        # Create directories
        input_dir = self.tmp_path / "reports"
        input_dir.mkdir(exist_ok=True)

        return AggregatorConfig(
            input_dir=input_dir,
            output_file=self.tmp_path / "output.json",
            verbose=self._verbose,
            scanner=self._scanner
        )

# Usage in tests
def test_with_builder(tmp_path):
    """Test using config builder pattern."""
    config = (
        ConfigBuilder(tmp_path)
        .with_verbose()
        .with_scanner("trivy")
        .build()
    )

    with config_context(config):
        # Test code
        pass
```

### Thread-Safe Configuration Access

```python
import threading
from cve_report_aggregator.config import get_current_config

def worker_function():
    """Worker thread that accesses configuration."""
    try:
        config = get_current_config()
        # Use config safely in thread
        if config.verbose:
            print(f"Thread {threading.current_thread().name}: Processing...")

    except ConfigurationError:
        print("Config not initialized")

# All threads can safely access the same config
threads = [threading.Thread(target=worker_function) for _ in range(10)]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()
```

### Configuration-Aware Logging Setup

```python
import logging
from cve_report_aggregator.config import get_current_config, is_config_initialized

def setup_logging():
    """Setup logging based on configuration."""
    # Determine log level from config
    log_level = logging.INFO
    if is_config_initialized():
        config = get_current_config()
        log_level = logging.DEBUG if config.verbose else logging.INFO

    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

# Call at application startup after set_config()
setup_logging()
```

### Conditional Feature Enablement

```python
from cve_report_aggregator.config import get_current_config

def process_with_features():
    """Process with conditional features based on config."""
    config = get_current_config()

    # Enable features based on configuration
    if config.mode == "highest-score":
        # Use CVSS score comparison
        use_cvss_comparison = True
    else:
        # Use first-occurrence
        use_cvss_comparison = False

    if config.scanner == "trivy":
        # Trivy-specific processing
        convert_to_cyclonedx = True
    else:
        # Grype-specific processing
        convert_to_cyclonedx = False

    # Process with enabled features
    # ...
```

## Common Patterns Summary

| Pattern              | Use Case             | Example                                  |
| -------------------- | -------------------- | ---------------------------------------- |
| **Simple Access**    | Most common case     | `config = get_current_config()`          |
| **Defensive Access** | Optional config      | `if is_config_initialized(): ...`        |
| **Context Manager**  | Testing              | `with config_context(test_config): ...`  |
| **Explicit Passing** | No global state      | `execute_command(cmd, config=config)`    |
| **Mixed Approach**   | Flexible API         | Try global, fallback to explicit         |
| **Builder Pattern**  | Complex test configs | `ConfigBuilder().with_verbose().build()` |

## Best Practices

1. **Initialize Once**: Call `set_config()` once at application startup
1. **Use Context Managers in Tests**: Automatically cleanup test state
1. **Check Initialization**: Use `is_config_initialized()` for optional access
1. **Handle Errors**: Catch `ConfigurationError` gracefully
1. **Prefer Global Config**: Use global config for simplicity, explicit passing for flexibility
1. **Document Config Usage**: Clearly document which functions require config
1. **Test Both Modes**: Test with and without global config initialized
1. **Reset in Tests**: Use `autouse=True` fixture to reset config between tests
