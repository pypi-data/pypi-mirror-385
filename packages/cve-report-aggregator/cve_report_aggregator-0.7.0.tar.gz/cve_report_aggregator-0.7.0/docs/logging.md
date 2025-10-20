# Logging System Documentation

This document describes the centralized logging system in CVE Report Aggregator using
[structlog](https://www.structlog.org/).

## Overview

The application uses a `LogManager` class to provide consistent, structured logging across all modules. The logging
system integrates with the global configuration to automatically set log levels based on the `verbose` flag.

### Key Features

- **Structured Logging**: All logs use structured data with key-value pairs for easier parsing and analysis
- **Global Configuration Integration**: Log levels automatically adjust based on `config.verbose` setting
- **Multiple Output Formats**: Support for colored console output (development) and JSON output (production)
- **Context Binding**: Attach contextual information to logs (request IDs, session IDs, etc.)
- **Thread-Safe**: Safe to use in concurrent environments
- **Type-Safe**: Full type hints with mypy checking

## Quick Start

### Basic Usage

```python
from cve_report_aggregator.logging import get_logger

# Get a logger for your module
logger = get_logger(__name__)

# Log messages with structured data
logger.info("Processing vulnerability", vuln_id="CVE-2024-12345", severity="High")
logger.debug("Scanning image", image="nginx:1.21", scanner="grype")
logger.error("Scan failed", error="Permission denied", image="nginx:1.21")
```

### With Exception Information

```python
try:
    process_vulnerability(vuln)
except Exception:
    logger.exception("Failed to process vulnerability", vuln_id=vuln.id)
```

## Configuration

### Automatic Configuration

The `LogManager` automatically configures itself on first use, reading settings from the global configuration:

```python
from cve_report_aggregator.config import set_config, get_config
from cve_report_aggregator.logging import LogManager

# Initialize global config
config = get_config(cli_args={'verbose': True})
set_config(config)

# LogManager will automatically use verbose=True → DEBUG level
LogManager.configure()
```

### Manual Configuration

For more control, configure explicitly:

```python
from cve_report_aggregator.logging import LogManager

# Configure with specific settings
LogManager.configure(
    log_level="DEBUG",     # DEBUG, INFO, WARNING, ERROR, CRITICAL
    use_json=False,        # Use JSON output format
    use_colors=True,       # Use colored console output
)
```

### Output Formats

#### Console Output (Default)

Colored, human-readable output for development:

```
2025-10-19T00:13:46.158966Z [info     ] Processing vulnerability   vuln_id=CVE-2024-12345 severity=High
2025-10-19T00:13:46.159012Z [debug    ] Scanning image             image=nginx:1.21 scanner=grype
```

#### JSON Output

Machine-parseable JSON for production/log aggregation:

```python
LogManager.configure(use_json=True)
```

```json
{"event": "Processing vulnerability", "level": "info", "timestamp": "2025-10-19T00:13:46.158966Z", "vuln_id": "CVE-2024-12345", "severity": "High"}
{"event": "Scanning image", "level": "debug", "timestamp": "2025-10-19T00:13:46.159012Z", "image": "nginx:1.21", "scanner": "grype"}
```

## Advanced Usage

### Context Binding

Attach context to a specific logger instance:

```python
from cve_report_aggregator.logging import get_logger

# Create logger with initial context
logger = get_logger(__name__, component="scanner", version="1.0")

# Or bind context to existing logger
logger = get_logger(__name__)
bound_logger = logger.bind(request_id="abc-123", user="admin")

# All messages from bound_logger include the context
bound_logger.info("Scan started")  # Includes request_id and user
bound_logger.info("Scan completed")  # Also includes request_id and user
```

### Global Context (Context Manager)

Apply context to all loggers within a scope:

```python
from cve_report_aggregator.logging import LogManager

with LogManager.log_context(request_id="abc-123", session="sess-456"):
    # All log messages in this block include request_id and session
    logger1 = get_logger("module1")
    logger1.info("Processing request")  # Includes request_id, session

    # Even from different modules
    logger2 = get_logger("module2")
    logger2.info("Validating input")  # Also includes request_id, session
```

### Dynamic Log Level Changes

Change log level at runtime:

```python
from cve_report_aggregator.logging import LogManager

# Start with INFO level
LogManager.configure(log_level="INFO")

# ... application runs ...

# Switch to DEBUG for troubleshooting
LogManager.set_log_level("DEBUG")

# Switch back to INFO
LogManager.set_log_level("INFO")
```

## Integration with Global Configuration

The logging system automatically respects the global configuration:

```python
from cve_report_aggregator.config import get_config, set_config
from cve_report_aggregator.logging import get_logger

# Load configuration
config = get_config(cli_args={'verbose': True})
set_config(config)

# Logger automatically uses DEBUG level
logger = get_logger(__name__)
logger.debug("This message will appear")  # Because verbose=True

# With verbose=False, DEBUG messages are filtered
config2 = get_config(cli_args={'verbose': False})
set_config(config2)
LogManager.reset()  # Reset to pick up new config

logger2 = get_logger(__name__)
logger2.debug("This message won't appear")  # Filtered out
logger2.info("This message will appear")  # INFO and above still shown
```

## Best Practices

### 1. Use Structured Logging

**Good** - Structured data is easy to parse and filter:

```python
logger.info(
    "Vulnerability found",
    vuln_id="CVE-2024-12345",
    severity="High",
    cvss_score=7.5,
    package="openssl",
    version="1.1.1k",
)
```

**Avoid** - String formatting loses structure:

```python
logger.info(f"Found {severity} vulnerability {vuln_id} in {package}")
```

### 2. Use Appropriate Log Levels

- **DEBUG**: Detailed diagnostic information, only when `verbose=True`
- **INFO**: General informational messages about application progress
- **WARNING**: Warning about potential issues that don't prevent operation
- **ERROR**: Error events that might allow application to continue
- **CRITICAL**: Severe errors that may cause application termination

```python
logger.debug("Cache hit", key="vuln_cache", hit_rate=0.95)
logger.info("Scan completed", duration_ms=1234, vulnerabilities=42)
logger.warning("Rate limit approaching", requests=950, limit=1000)
logger.error("Failed to connect to registry", registry="ghcr.io", error=str(e))
```

### 3. Include Contextual Information

Always include relevant context to make logs actionable:

```python
# Good - includes actionable context
logger.error(
    "Failed to scan image",
    image="nginx:1.21",
    scanner="grype",
    error=str(e),
    retry_count=3,
)

# Less useful - missing context
logger.error("Scan failed")
```

### 4. Use Exception Logging

Use `logger.exception()` in exception handlers to include stack traces:

```python
try:
    scan_image(image)
except Exception:
    logger.exception("Scan failed", image=image, scanner="grype")
```

### 5. Module-Level Logger

Create loggers at module level, not function level:

```python
# Good - module level
from cve_report_aggregator.logging import get_logger

logger = get_logger(__name__)

def process_vulnerability(vuln):
    logger.info("Processing", vuln_id=vuln.id)

# Avoid - function level (creates many logger instances)
def process_vulnerability(vuln):
    logger = get_logger(__name__)  # Don't do this
    logger.info("Processing", vuln_id=vuln.id)
```

## Testing with Logging

The logging system includes test utilities:

```python
import pytest
from cve_report_aggregator.logging import LogManager, get_logger

@pytest.fixture(autouse=True)
def reset_logging():
    """Reset logging state before each test."""
    LogManager.reset()
    yield
    LogManager.reset()

def test_my_function(capsys):
    """Test function that uses logging."""
    LogManager.configure(log_level="DEBUG")
    logger = get_logger(__name__)

    logger.info("Test message", key="value")

    captured = capsys.readouterr()
    assert "Test message" in captured.out
    assert "key" in captured.out
    assert "value" in captured.out
```

## Architecture

### Class Diagram

```bash
┌─────────────────────────────────────────────┐
│           LogManager                        │
├─────────────────────────────────────────────┤
│ - _configured: bool                         │
│ - _loggers: dict[str, FilteringBoundLogger] │
├─────────────────────────────────────────────┤
│ + configure(log_level, use_json, ...)       │
│ + get_logger(name, **context)               │
│ + reset()                                   │
│ + log_context(**context)                    │
│ + get_log_level() -> str                    │
│ + set_log_level(level)                      │
└─────────────────────────────────────────────┘
         │
         │ creates
         ▼
┌─────────────────────────────────────────────┐
│    FilteringBoundLogger (structlog)         │
├─────────────────────────────────────────────┤
│ + info(event, **kw)                         │
│ + debug(event, **kw)                        │
│ + warning(event, **kw)                      │
│ + error(event, **kw)                        │
│ + exception(event, **kw)                    │
│ + bind(**kw) -> FilteringBoundLogger        │
└─────────────────────────────────────────────┘
```

### Processor Chain

Logs flow through the following processors:

1. **merge_contextvars** - Merges context from `log_context()` calls
1. **add_log_level** - Adds log level to event dict
1. **TimeStamper** - Adds ISO timestamp
1. **StackInfoRenderer** - Adds stack information for exceptions
1. **format_exc_info** - Formats exception tracebacks
1. **UnicodeDecoder** - Ensures proper unicode handling
1. **ConsoleRenderer** or **JSONRenderer** - Final output formatting

## Migration Guide

### From Standard Library Logging

If you have code using Python's standard `logging` module:

**Before:**

```python
import logging

logger = logging.getLogger(__name__)

def process_data(data):
    logger.info("Processing data with ID %s", data.id)
    try:
        result = expensive_operation(data)
        logger.debug("Result: %s", result)
    except Exception as e:
        logger.error("Failed: %s", e)
```

**After:**

```python
from cve_report_aggregator.logging import get_logger

logger = get_logger(__name__)

def process_data(data):
    logger.info("Processing data", data_id=data.id)
    try:
        result = expensive_operation(data)
        logger.debug("Operation completed", result=result)
    except Exception:
        logger.exception("Operation failed", data_id=data.id)
```

### Key Changes

1. Replace `logging.getLogger(__name__)` with `get_logger(__name__)`
1. Use keyword arguments instead of string formatting
1. Use `logger.exception()` instead of `logger.error()` with exception info
1. Remove `logger.setLevel()` - use global configuration instead

## API Reference

### LogManager Class

#### `LogManager.configure(log_level=None, use_json=False, use_colors=True)`

Configure structlog with application-wide settings.

**Parameters:**

- `log_level` (str | None): Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `use_json` (bool): Use JSON output format
- `use_colors` (bool): Use colored console output

**Example:**

```python
LogManager.configure(log_level="DEBUG", use_json=False)
```

#### `LogManager.get_logger(name=None, **initial_context)`

Get a configured structlog logger.

**Parameters:**

- `name` (str | None): Logger name (typically `__name__`)
- `**initial_context`: Initial context to bind

**Returns:** `FilteringBoundLogger`

**Example:**

```python
logger = LogManager.get_logger(__name__, component="scanner")
```

#### `LogManager.log_context(**context)`

Context manager for temporarily binding context.

**Parameters:**

- `**context`: Context key-value pairs

**Example:**

```python
with LogManager.log_context(request_id="abc-123"):
    logger.info("Processing")  # Includes request_id
```

#### `LogManager.reset()`

Reset LogManager state (useful for testing).

#### `LogManager.get_log_level() -> str`

Get current log level from configuration.

#### `LogManager.set_log_level(level: str)`

Dynamically change log level.

### Convenience Functions

#### `get_logger(name=None, **context)`

Shorthand for `LogManager.get_logger()`.

**Example:**

```python
from cve_report_aggregator.logging import get_logger

logger = get_logger(__name__)
```

## Troubleshooting

### Logs Not Appearing

**Problem:** Debug logs don't appear even with `verbose=True`

**Solution:** Ensure global config is initialized before creating loggers:

```python
# Initialize config FIRST
config = get_config(cli_args={'verbose': True})
set_config(config)

# THEN get logger
logger = get_logger(__name__)
```

### JSON Output Not Working

**Problem:** Still seeing console output instead of JSON

**Solution:** Configure before first logger creation:

```python
# Configure BEFORE getting any loggers
LogManager.configure(use_json=True)

logger = get_logger(__name__)
```

### Context Not Appearing in Logs

**Problem:** Context from `log_context()` not showing in output

**Solution:** Ensure `merge_contextvars` processor is in the chain (automatically included).

## Performance Considerations

- Loggers are cached by name for efficiency
- Use log level filtering to avoid expensive operations in production:

```python
# Good - only evaluates if DEBUG enabled
logger.debug("Complex data", data=expensive_serialization(obj))

# Better - conditional check for expensive operations
if config.verbose:
    logger.debug("Complex data", data=expensive_serialization(obj))
```

## Further Reading

- [structlog Documentation](https://www.structlog.org/)
- [Structured Logging Best Practices](https://www.structlog.org/en/stable/why.html)
- [Configuration Management](./configuration/overview.md)
