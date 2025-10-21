"""Custom exceptions for CVE report aggregation.

This module provides a hierarchy of custom exceptions that improve
error handling and make it easier to catch and handle specific error
conditions throughout the application.
"""


class CVEAggregatorError(Exception):
    """Base exception for all CVE aggregator errors.

    All custom exceptions in this application should inherit from this base class.
    """

    pass


class ConfigurationError(CVEAggregatorError):
    """Raised when configuration is invalid or missing.

    Examples:
        - Required configuration field is missing
        - Configuration file is malformed
        - Invalid configuration values
    """

    pass


class ScannerError(CVEAggregatorError):
    """Base exception for scanner-related errors."""

    pass


class ScannerNotFoundError(ScannerError):
    """Raised when a required scanner tool is not installed or not found in PATH.

    This includes tools like grype, syft, trivy, and uds.
    """

    def __init__(self, scanner: str, message: str | None = None) -> None:
        """Initialize scanner not found error.

        Args:
            scanner: Name of the scanner tool that was not found
            message: Optional custom error message
        """
        self.scanner = scanner
        if message is None:
            message = f"Scanner '{scanner}' not found. Please install it before running the aggregator."
        super().__init__(message)


class ScannerExecutionError(ScannerError):
    """Raised when a scanner command fails during execution.

    This includes errors like:
    - Scanner crashes
    - Invalid scanner output
    - Scanner returns non-zero exit code
    """

    def __init__(self, scanner: str, command: list[str], stderr: str | None = None) -> None:
        """Initialize scanner execution error.

        Args:
            scanner: Name of the scanner that failed
            command: The command that was executed
            stderr: Standard error output from the scanner
        """
        self.scanner = scanner
        self.command = command
        self.stderr = stderr
        message = f"Scanner '{scanner}' execution failed: {' '.join(command)}"
        if stderr:
            message += f"\nStderr: {stderr}"
        super().__init__(message)


class ReportError(CVEAggregatorError):
    """Base exception for report-related errors."""

    pass


class ReportLoadError(ReportError):
    """Raised when a report file cannot be loaded or parsed.

    Examples:
        - JSON parse errors
        - Invalid report format
        - Missing required fields
    """

    def __init__(self, file_path: str, reason: str) -> None:
        """Initialize report load error.

        Args:
            file_path: Path to the report file that failed to load
            reason: Description of why the load failed
        """
        self.file_path = file_path
        self.reason = reason
        super().__init__(f"Failed to load report '{file_path}': {reason}")


class ReportValidationError(ReportError):
    """Raised when a report has invalid or unexpected structure.

    Examples:
        - Missing required fields
        - Invalid data types
        - Unexpected report format
    """

    pass


class DownloadError(CVEAggregatorError):
    """Raised when downloading SBOM reports from remote registry fails.

    Examples:
        - Network errors
        - Authentication failures
        - Package not found in registry
    """

    def __init__(self, package: str, reason: str) -> None:
        """Initialize download error.

        Args:
            package: Name of the package that failed to download
            reason: Description of why the download failed
        """
        self.package = package
        self.reason = reason
        super().__init__(f"Failed to download SBOM for package '{package}': {reason}")


class AggregationError(CVEAggregatorError):
    """Raised when vulnerability deduplication/aggregation fails.

    Examples:
        - Data inconsistencies
        - Invalid vulnerability data
        - Aggregation logic errors
    """

    pass
