# Configuration Management Architecture

This document explains the configuration management system in CVE Report Aggregator, including design patterns, usage
examples, and testing strategies.

## Overview

The configuration management system provides a **thread-safe, singleton-based global configuration** that can be shared
across modules without explicit parameter passing. This pattern simplifies the codebase while maintaining testability
and type safety.

## Design Pattern: Context-Based Singleton

### Pattern Choice Rationale

We chose a **module-level singleton with context manager support** for the following reasons:

1. **Simplicity**: Simple to understand and use - set once, access anywhere
1. **Thread Safety**: Uses `threading.Lock()` to ensure safe concurrent access
1. **Testability**: Context managers allow easy test isolation without global state pollution
1. **Type Safety**: Full type hints with Pydantic validation
1. **No Circular Imports**: Uses `TYPE_CHECKING` for type hints in executor module
1. **Explicit Initialization**: Fails fast with clear error messages if accessed before initialization

### Comparison with Alternatives

| Pattern                | Pros                    | Cons                                | Our Choice                        |
| ---------------------- | ----------------------- | ----------------------------------- | --------------------------------- |
| Module-level singleton | Simple, fast access     | Global state concerns               | ✅ Chosen (with context managers) |
| Dependency injection   | Most testable, explicit | Verbose, parameter passing overhead | Too verbose                       |
| Class-based singleton  | Encapsulation           | Metaclass complexity                | Unnecessary complexity            |
| Environment variables  | Simple                  | No validation, type coercion        | Already used for initial loading  |
| Global instance        | Fastest                 | Hard to test                        | Not testable                      |

## Architecture Components

### 1. Configuration Loading (`config.py`)

```python
# Load configuration from multiple sources
config = get_config(
    cli_args={'verbose': True},
    config_file_path=Path('./config.yaml')
)
```

**Priority order** (highest to lowest):

1. CLI arguments (passed to `get_config()`)
1. YAML configuration file
1. Environment variables (`CVE_AGGREGATOR_*`)
1. Default values

### 2. Global Configuration Manager

#### Setting Configuration (Application Startup)

```python
from cve_report_aggregator.config import get_config, set_config

# In main() or application entry point
config = get_config(cli_args={'verbose': True})
set_config(config)  # Initialize global singleton
```

#### Accessing Configuration (Any Module)

```python
from cve_report_aggregator.config import get_current_config

# Anywhere in the codebase
config = get_current_config()
print(f"Verbose: {config.verbose}")
print(f"Scanner: {config.scanner}")
```

#### Checking Initialization Status

```python
from cve_report_aggregator.config import is_config_initialized, get_current_config

# Defensive pattern for optional config access
if is_config_initialized():
    config = get_current_config()
    # Use config...
else:
    # Fallback behavior
    pass
```

### 3. Testing Support

#### Context Manager for Test Isolation

```python
from cve_report_aggregator.config import config_context
from cve_report_aggregator.models import AggregatorConfig

def test_my_feature(tmp_path):
    # Create test configuration
    test_config = AggregatorConfig(
        input_dir=tmp_path / "reports",
        output_file=tmp_path / "output.json",
        verbose=True
    )

    # Use context manager for isolated test
    with config_context(test_config):
        # Test code that needs config
        assert get_current_config().verbose is True

    # Config is automatically cleaned up after context
```

#### Pytest Fixture for Clean State

```python
import pytest
from cve_report_aggregator.config import reset_config

@pytest.fixture(autouse=True)
def reset_global_config():
    """Ensure clean config state before each test."""
    reset_config()
    yield
    reset_config()
```

## Thread Safety

The configuration manager uses `threading.Lock()` to ensure thread-safe operations:

```python
_config_lock = threading.Lock()

def set_config(config: AggregatorConfig) -> None:
    global _config
    with _config_lock:
        _config = config

def get_current_config() -> AggregatorConfig:
    if _config is None:
        raise ConfigurationError("Config not initialized")
    return _config  # Read-only access, no lock needed
```

### Thread Safety Guarantees

- **Set operations**: Locked to prevent race conditions
- **Get operations**: Safe because Pydantic models are immutable after creation
- **Context managers**: Locked for proper state restoration
- **Concurrent access**: Multiple threads can safely read configuration simultaneously

## Usage Examples

### Application Startup (cli.py)

```python
def main(input_dir, output_file, scanner, verbose, mode):
    """CLI entry point."""
    # 1. Build CLI arguments
    cli_args = {
        'input_dir': input_dir,
        'output_file': output_file,
        'scanner': scanner,
        'verbose': verbose,
        'mode': mode,
    }

    # 2. Load and validate configuration from all sources
    app_config = get_config(cli_args=cli_args)

    # 3. Set as global configuration for sharing
    set_config(app_config)

    # 4. Now all modules can access config
    # ... rest of application logic
```

### Module Access (executor.py)

```python
def execute_command_with_global_config(
    command: list[str],
    cwd: str | Path | None = None,
) -> tuple[str, Exception | None]:
    """Execute command using global configuration."""
    from .config import get_current_config, is_config_initialized

    # Try to use global config if available
    config = None
    if is_config_initialized():
        try:
            config = get_current_config()
        except Exception as e:
            logger.warning("Failed to get global config: %s", e)

    return execute_command(command, cwd=cwd, config=config)
```

### Explicit Config Passing (Alternative Pattern)

```python
def execute_command(
    command: list[str],
    cwd: str | Path | None = None,
    config: AggregatorConfig | None = None,
) -> tuple[str, Exception | None]:
    """Execute command with optional config override."""
    # Determine working directory
    if cwd is None and config is not None:
        cwd = config.input_dir.parent

    # Determine log level
    log_level = logging.DEBUG if (config and config.verbose) else logging.INFO

    # ... execute command
```

### Testing with Mock Config

```python
def test_executor_with_verbose_config(tmp_path):
    """Test executor with verbose logging enabled."""
    from cve_report_aggregator.executor import execute_command
    from cve_report_aggregator.models import AggregatorConfig

    # Create test config
    test_config = AggregatorConfig(
        input_dir=tmp_path / "reports",
        output_file=tmp_path / "output.json",
        verbose=True
    )

    # Use context manager
    with config_context(test_config):
        output, error = execute_command(["echo", "test"])
        assert error is None
        assert "test" in output
```

## Error Handling

### Configuration Not Initialized

```python
from cve_report_aggregator.config import ConfigurationError

try:
    config = get_current_config()
except ConfigurationError as e:
    print(f"Error: {e}")
    # Handle uninitialized config
```

**Error message**:

```bash
Global configuration not initialized.
Call set_config() at application startup before accessing configuration.
```

### Validation Errors

```python
from pydantic import ValidationError

try:
    config = get_config(cli_args={'input_dir': '/nonexistent'})
except ValidationError as e:
    print("Configuration validation failed:")
    for error in e.errors():
        print(f"  {error['loc']}: {error['msg']}")
```

## Best Practices

### ✅ Do

1. **Initialize once at application startup**

   ```python
   # In main()
   config = get_config(cli_args=cli_args)
   set_config(config)
   ```

1. **Use context managers in tests**

   ```python
   with config_context(test_config):
       # Test code
       pass
   ```

1. **Check initialization status when appropriate**

   ```python
   if is_config_initialized():
       config = get_current_config()
   ```

1. **Use type hints for config parameters**

   ```python
   def my_function(config: AggregatorConfig | None = None) -> None:
       pass
   ```

### Don't

1. **Don't call `set_config()` multiple times in production**

   ```python
   # Bad: Setting config in multiple places
   set_config(config1)
   # ... later
   set_config(config2)  # Unexpected override
   ```

1. **Don't use `reset_config()` outside of tests**

   ```python
   # Bad: Resetting in production code
   reset_config()  # Will break other modules
   ```

1. **Don't modify config after setting it**

   ```python
   # Bad: Mutating global state
   config = get_current_config()
   config.verbose = True  # Won't work - Pydantic models are validated on assignment
   ```

1. **Don't ignore `ConfigurationError`**

   ```python
   # Bad: Silently catching errors
   try:
       config = get_current_config()
   except:
       pass  # Silent failure
   ```

## Performance Characteristics

- **Memory**: Single instance shared across all modules
- **Access Time**: O(1) dictionary lookup with threading lock
- **Thread Safety**: Minimal overhead - read operations don't require locks
- **Initialization**: One-time cost at application startup
- **Testing Overhead**: Context managers have minimal performance impact

## Testing Strategies

### Unit Testing

```python
class TestMyModule:
    """Test module with configuration."""

    @pytest.fixture(autouse=True)
    def reset_config(self):
        """Reset config before each test."""
        reset_config()
        yield
        reset_config()

    def test_with_config(self, tmp_path):
        """Test with specific configuration."""
        config = AggregatorConfig(
            input_dir=tmp_path / "reports",
            output_file=tmp_path / "output.json",
            verbose=True
        )

        with config_context(config):
            # Test code
            assert get_current_config().verbose is True
```

### Integration Testing

```python
def test_full_workflow(tmp_path):
    """Test complete workflow with configuration."""
    from cve_report_aggregator.config import get_config, set_config

    # Create test environment
    (tmp_path / "reports").mkdir()

    # Initialize like production
    config = get_config(cli_args={
        'input_dir': tmp_path / "reports",
        'output_file': tmp_path / "output.json",
        'verbose': True
    })
    set_config(config)

    # Run workflow
    # ...

    # Cleanup
    reset_config()
```

### Mocking for External Dependencies

```python
from unittest.mock import patch

def test_with_mocked_config_loading(tmp_path):
    """Test with mocked configuration loading."""
    mock_config = AggregatorConfig(
        input_dir=tmp_path / "reports",
        output_file=tmp_path / "output.json"
    )

    with patch('cve_report_aggregator.config.get_config', return_value=mock_config):
        # Test code that calls get_config()
        pass
```

## Troubleshooting

### Issue: ConfigurationError on startup

**Problem**: `Global configuration not initialized` error

**Solution**: Ensure `set_config()` is called in `main()` before any module tries to access config

```python
# In cli.py main()
config = get_config(cli_args=cli_args)
set_config(config)  # Must be called before other modules access config
```

### Issue: Tests interfering with each other

**Problem**: Global config leaking between tests

**Solution**: Use `autouse=True` fixture to reset config

```python
@pytest.fixture(autouse=True)
def reset_global_config():
    reset_config()
    yield
    reset_config()
```

### Issue: Type checking errors

**Problem**: Circular import when importing `AggregatorConfig` in executor

**Solution**: Use `TYPE_CHECKING` for type-only imports

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import AggregatorConfig

def execute_command(config: AggregatorConfig | None = None) -> None:
    pass
```

## Future Enhancements

Potential improvements to consider:

1. **Configuration Versioning**: Track config version for migrations
1. **Configuration Change Events**: Notify modules when config changes
1. **Configuration Snapshots**: Save/restore config state for rollback
1. **Configuration Profiles**: Support multiple named configurations
1. **Configuration Validation Hooks**: Custom validation logic for specific use cases

## References

- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Python Threading Documentation](https://docs.python.org/3/library/threading.html)
- [Context Managers PEP 343](https://peps.python.org/pep-0343/)
- [Type Checking Best Practices](https://typing.readthedocs.io/en/latest/source/best_practices.html)
