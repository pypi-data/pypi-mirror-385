"""Command executor module with configuration-aware execution.

This module provides an ExecutorManager class for consistent command execution
across the entire application. It integrates with the global configuration
system and provides structured logging for all command executions.

Features:
- Configuration-aware command execution
- Automatic working directory management
- Structured logging with verbosity control
- Thread-safe operation
- Comprehensive error handling
- Support for both synchronous execution

Example:
    >>> from cve_report_aggregator.executor import ExecutorManager
    >>> # Execute with global config
    >>> output, error = ExecutorManager.execute(["grype", "--version"])
    >>> if error:
    ...     print(f"Command failed: {error}")

    >>> # Execute with explicit config
    >>> from cve_report_aggregator.config import get_config
    >>> config = get_config()
    >>> output, error = ExecutorManager.execute(
    ...     ["git", "status"],
    ...     cwd="/tmp",
    ...     config=config
    ... )
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

from .logging import get_logger

if TYPE_CHECKING:
    from .models import AggregatorConfig

logger = get_logger(__name__)


class ExecutorManager:
    """Centralized command execution manager.

    This class provides a singleton-style interface for executing shell commands
    with consistent error handling, logging, and configuration integration.

    All command execution should go through this manager to ensure:
    - Consistent error handling and logging
    - Configuration-aware defaults (working directory, verbosity)
    - Structured logging of command execution
    - Proper error propagation and reporting
    """

    @classmethod
    def execute(
        cls,
        command: list[str],
        cwd: str | Path | None = None,
        config: AggregatorConfig | None = None,
    ) -> tuple[str, Exception | None]:
        """Execute a command in the shell with configuration-aware defaults.

        This method executes shell commands with optional working directory and
        configuration context. If a config is provided, it will use config.cwd as
        the default working directory and adjust logging based on config.log_level.

        Args:
            command: The command to execute as a list of strings
            cwd: Working directory for the command (overrides config.cwd if provided)
            config: Optional configuration for defaults (uses global config if None)

        Returns:
            Tuple of (stdout, error) where error is None on success or Exception on failure

        Example:
            >>> # Use global config (if initialized)
            >>> output, error = ExecutorManager.execute(["ls", "-la"])
            >>> if error:
            ...     print(f"Command failed: {error}")

            >>> # Provide explicit config
            >>> from .config import get_config
            >>> config = get_config()
            >>> output, error = ExecutorManager.execute(["grype", "--version"], config=config)

            >>> # Override working directory
            >>> output, error = ExecutorManager.execute(
            ...     ["git", "status"],
            ...     cwd="/tmp",
            ...     config=config
            ... )
        """
        # Determine working directory
        working_dir: str | Path | None = cwd
        if working_dir is None and config is not None:
            # Use config.cwd as fallback if no explicit cwd provided
            # Note: We use Path.cwd() from config, but it's already a Path
            working_dir = config.input_dir.parent if hasattr(config, "input_dir") else None

        # Convert Path to string for subprocess
        working_dir_str: str | None = str(working_dir) if working_dir else None

        # Log command execution (structlog will handle verbosity via config)
        is_debug = config and config.log_level == "DEBUG"
        if is_debug:
            logger.debug("Executing command", command=" ".join(command), cwd=working_dir_str)
        else:
            logger.info("Executing command", command=" ".join(command))

        try:
            # Capture stdout and stderr and return them
            result: subprocess.CompletedProcess[str] = subprocess.run(
                command,
                cwd=working_dir_str,
                check=True,
                text=True,
                capture_output=True,
            )

            if is_debug and result.stdout:
                # Log first 500 chars of output
                logger.debug("Command output", output=result.stdout[:500])

            return result.stdout, None

        except subprocess.CalledProcessError as e:
            logger.error(
                "Command execution failed",
                command=" ".join(command),
                return_code=e.returncode,
                stderr=e.stderr if e.stderr else None,
            )

            # Return combined stdout + stderr for error context
            return e.stdout + e.stderr, e

        except FileNotFoundError as e:
            logger.error("Command not found", command=command[0], error=str(e))
            return "", e

        except Exception as e:
            logger.error("Unexpected error executing command", command=" ".join(command), error=str(e))
            return "", e

    @classmethod
    def execute_with_global_config(
        cls,
        command: list[str],
        cwd: str | Path | None = None,
    ) -> tuple[str, Exception | None]:
        """Execute a command using the global configuration.

        This is a convenience method that automatically uses the global configuration
        if it's been initialized. If the global config is not available, it falls back
        to basic execution without config-aware features.

        Args:
            command: The command to execute as a list of strings
            cwd: Optional working directory (overrides config.cwd if provided)

        Returns:
            Tuple of (stdout, error) where error is None on success or Exception on failure

        Example:
            >>> # After initializing global config in main()
            >>> from .config import get_config, set_config
            >>> config = get_config(cli_args={'log_level': 'DEBUG'})
            >>> set_config(config)
            >>>
            >>> # Now execute commands anywhere in the codebase
            >>> output, error = ExecutorManager.execute_with_global_config(["grype", "--version"])
        """
        from .config import get_current_config, is_config_initialized

        # Try to use global config if available
        config: AggregatorConfig | None = None
        if is_config_initialized():
            try:
                config = get_current_config()
            except Exception as e:
                logger.warning("Failed to get global config", error=str(e))

        return cls.execute(command, cwd=cwd, config=config)

    @classmethod
    def create_temp_directory(cls, config: AggregatorConfig | None = None) -> tuple[Path, Exception | None]:
        """Create a temporary directory using mktemp.

        Args:
            config: Optional configuration for logging

        Returns:
            Tuple of (temp_dir_path, error) where error is None on success

        Example:
            >>> temp_dir, error = ExecutorManager.create_temp_directory()
            >>> if not error:
            ...     print(f"Created temp dir: {temp_dir}")
        """
        output, error = cls.execute(["mktemp", "-d"], config=config)
        if error:
            return Path(), error
        return Path(output.strip()), None


# Public API
__all__ = [
    "ExecutorManager",
]
