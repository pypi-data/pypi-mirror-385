"""Core infrastructure modules for CVE Report Aggregator.

This package contains foundational components:
- Configuration management
- Logging infrastructure
- Command execution
- Data models and types
"""

from .config import (
    AggregatorSettings,
    ConfigurationError,
    config_context,
    get_config,
    get_current_config,
    is_config_initialized,
    load_settings,
    reset_config,
    set_config,
)
from .executor import ExecutorManager, execute_command, execute_command_with_global_config
from .logging import LogManager, get_logger
from .models import AggregatorConfig, ModeType, PackageConfig, ScannerType

__all__ = [
    # Config
    "AggregatorSettings",
    "ConfigurationError",
    "config_context",
    "get_config",
    "get_current_config",
    "is_config_initialized",
    "load_settings",
    "reset_config",
    "set_config",
    # Executor
    "ExecutorManager",
    "execute_command",
    "execute_command_with_global_config",
    # Logging
    "LogManager",
    "get_logger",
    # Models
    "AggregatorConfig",
    "ModeType",
    "PackageConfig",
    "ScannerType",
]
