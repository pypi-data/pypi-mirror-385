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
        the default working directory and adjust logging based on config.verbose.

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
        if config and config.verbose:
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

            if config and config.verbose and result.stdout:
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
            >>> config = get_config(cli_args={'verbose': True})
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
    def check_command_exists(cls, command: str) -> bool:
        """Check if a command exists in PATH.

        Args:
            command: Name of the command to check

        Returns:
            True if command exists, False otherwise

        Example:
            >>> if ExecutorManager.check_command_exists("grype"):
            ...     print("Grype is installed")
        """
        try:
            cls.execute(["which", command])
            return True
        except Exception:
            return False

    @classmethod
    def get_command_version(cls, command: str, version_flag: str = "version") -> str:
        """Get the version of a command.

        Args:
            command: Name of the command
            version_flag: Flag to get version (default: "version")

        Returns:
            Version string or "unknown" if unable to determine

        Example:
            >>> version = ExecutorManager.get_command_version("grype")
            >>> print(f"Grype version: {version}")
        """
        try:
            output, error = cls.execute([command, version_flag])
            if error:
                return "unknown"

            # Parse version from output
            # Try to extract version from common patterns
            for line in output.split("\n"):
                if "Version:" in line:
                    return line.split("Version:")[-1].strip()
                if "version" in line.lower():
                    # Try to extract semantic version pattern
                    import re

                    match = re.search(r"\d+\.\d+\.\d+", line)
                    if match:
                        return match.group(0)

            return "unknown"

        except Exception:
            return "unknown"

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


# Convenience functions for backward compatibility
def execute_command(
    command: list[str],
    cwd: str | Path | None = None,
    config: AggregatorConfig | None = None,
) -> tuple[str, Exception | None]:
    """Execute a command in the shell with configuration-aware defaults.

    This is a convenience function that delegates to ExecutorManager.execute().

    Args:
        command: The command to execute as a list of strings
        cwd: Working directory for the command (overrides config.cwd if provided)
        config: Optional configuration for defaults (uses global config if None)

    Returns:
        Tuple of (stdout, error) where error is None on success or Exception on failure

    Example:
        >>> from cve_report_aggregator.executor import execute_command
        >>> output, error = execute_command(["ls", "-la"])
    """
    return ExecutorManager.execute(command, cwd=cwd, config=config)


def execute_command_with_global_config(
    command: list[str],
    cwd: str | Path | None = None,
) -> tuple[str, Exception | None]:
    """Execute a command using the global configuration.

    This is a convenience function that delegates to ExecutorManager.execute_with_global_config().

    Args:
        command: The command to execute as a list of strings
        cwd: Optional working directory (overrides config.cwd if provided)

    Returns:
        Tuple of (stdout, error) where error is None on success or Exception on failure

    Example:
        >>> from cve_report_aggregator.executor import execute_command_with_global_config
        >>> output, error = execute_command_with_global_config(["grype", "--version"])
    """
    return ExecutorManager.execute_with_global_config(command, cwd=cwd)


# Public API
__all__ = [
    "ExecutorManager",
    "execute_command",
    "execute_command_with_global_config",
]
