"""Data models and type definitions for CVE report aggregation."""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator

# Type aliases for better type hints
ScannerType = Literal["grype", "trivy"]
ModeType = Literal["highest-score", "first-occurrence", "grype-only", "trivy-only"]
LogLevelType = Literal["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class PackageConfig(BaseModel):
    """Configuration for a package to scan.

    Attributes:
        name: Package name
        version: Package version
        architecture: Package architecture (e.g., amd64, arm64)
    """

    name: str = Field(description="Package name")
    version: str = Field(description="Package version")
    architecture: str = Field(default="amd64", description="Package architecture")


class EnrichmentConfig(BaseModel):
    """Configuration for CVE enrichment with OpenAI.

    Attributes:
        enabled: Enable CVE enrichment
        provider: Enrichment provider (only openai supported currently)
        model: OpenAI model to use (e.g., gpt-5-nano, gpt-5-mini, gpt-4o)
        api_key: OpenAI API key
        reasoning_effort: Reasoning effort level (minimal, low, medium, high)
        severities: List of severity levels to enrich
        verbosity: Verbosity level for model responses (low, medium, high)
        max_completion_tokens: Optional upper bound for total tokens
        seed: Optional seed for reproducible results
        metadata: Optional metadata tags for OpenAI requests
    """

    enabled: bool = Field(default=False, description="Enable CVE enrichment")
    provider: Literal["openai"] = Field(default="openai", description="Enrichment provider (only openai supported)")
    model: str = Field(default="gpt-5-nano", description="OpenAI model to use")
    api_key: str | None = Field(default=None, validation_alias="apiKey", description="OpenAI API key")
    reasoning_effort: str = Field(
        default="medium",
        validation_alias="reasoningEffort",
        pattern="^(minimal|low|medium|high)$",
        description="Reasoning effort level",
    )
    severities: list[str] = Field(
        default=["Critical", "High"],
        description="Severity levels to enrich",
    )
    verbosity: str = Field(
        default="medium",
        pattern="^(low|medium|high)$",
        description="Verbosity level for model responses",
    )
    max_completion_tokens: int | None = Field(
        default=None,
        validation_alias="maxCompletionTokens",
        description="Optional upper bound for total tokens including reasoning tokens",
    )
    seed: int | None = Field(
        default=None,
        description="Optional seed for reproducible results",
    )
    metadata: dict[str, str] | None = Field(
        default=None,
        description="Optional metadata tags for OpenAI requests",
    )

    class Config:
        """Pydantic configuration."""

        validate_assignment = True
        populate_by_name = True

    def __repr__(self) -> str:
        """Custom repr that redacts the API key for security.

        Returns:
            String representation with redacted API key
        """
        # Get the default repr
        default_repr: str = super().__repr__()

        # If api_key is set, replace it with <REDACTED>
        if self.api_key:
            # Replace the actual API key value with <REDACTED>
            redacted_repr: str = default_repr.replace(f"api_key='{self.api_key}'", "api_key='<REDACTED>'")
            return redacted_repr

        return default_repr


class AggregatorConfig(BaseModel):
    """Configuration model for CVE Report Aggregator.

    This model provides comprehensive validation of all configuration
    parameters including paths, scanner selection, and operational modes.

    Attributes:
        input_dir: Directory containing scan report files
        output_file: Path for the unified output report
        scanner: Scanner type to use (grype or trivy)
        mode: Aggregation mode for vulnerability processing
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        config_file: Optional path to YAML configuration file
        registry: Container registry URL
        organization: Organization or namespace in the registry
        packages: List of packages to scan
        downloadRemotePackages: Download SBOM reports from remote registry
        enrich: CVE enrichment configuration (nested)
    """

    input_dir: Path = Field(
        default=Path.cwd() / "reports",
        description="Input directory containing scan report files",
        validation_alias="inputDir",
    )
    output_file: Path = Field(
        default=Path.cwd() / "unified-report.json",
        description="Output file path for the unified report",
        validation_alias="outputFile",
    )
    scanner: ScannerType = Field(
        default="grype",
        description="Vulnerability scanner to use",
    )
    mode: ModeType = Field(
        default="highest-score",
        description="Aggregation mode for vulnerability processing",
    )
    log_level: LogLevelType = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
        validation_alias="logLevel",
    )
    config_file: Path | None = Field(
        default=None,
        description="Path to YAML configuration file",
        validation_alias="configFile",
    )
    registry: str | None = Field(
        default=None,
        description="Container registry URL",
    )
    organization: str | None = Field(
        default=None,
        description="Organization or namespace in the registry",
    )
    packages: list[PackageConfig] = Field(
        default_factory=list,
        description="List of packages to scan",
    )
    download_remote_packages: bool = Field(
        default=False,
        description="Download SBOM reports from remote registry for specified packages",
        validation_alias="downloadRemotePackages",
    )
    max_workers: int | None = Field(
        default=None,
        description=(
            "Maximum number of concurrent workers for parallel operations (default: auto-detect based on CPU count)"
        ),
        validation_alias="maxWorkers",
    )

    # CVE enrichment configuration (nested)
    enrich: EnrichmentConfig = Field(
        default_factory=EnrichmentConfig,
        description="CVE enrichment configuration",
    )

    class Config:
        """Pydantic configuration."""

        validate_assignment = True
        frozen = False
        populate_by_name = True  # Allow both alias and field name

    def __repr__(self) -> str:
        """Custom repr that redacts the API key for security.

        Returns:
            String representation with redacted API key in nested EnrichmentConfig
        """
        # Get the default repr
        default_repr: str = super().__repr__()

        # If enrichment config has an API key, it will already be redacted by EnrichmentConfig.__repr__()
        # However, the parent repr doesn't use the child's __repr__, so we need to manually redact
        if self.enrich.api_key:
            # Replace any occurrence of the actual API key with <REDACTED>
            redacted_repr: str = default_repr.replace(f"api_key='{self.enrich.api_key}'", "api_key='<REDACTED>'")
            return redacted_repr

        return default_repr

    @field_validator("input_dir")
    @classmethod
    def validate_input_dir(cls, v: Path) -> Path:
        """Validate that input directory exists and is accessible.

        Args:
            v: Input directory path

        Returns:
            Validated and resolved Path object

        Raises:
            ValueError: If directory doesn't exist or isn't accessible
        """
        resolved = v.resolve()
        if not resolved.exists():
            raise ValueError(f"Input directory does not exist: {resolved}")
        if not resolved.is_dir():
            raise ValueError(f"Input path is not a directory: {resolved}")
        return resolved

    @field_validator("output_file")
    @classmethod
    def validate_output_file(cls, v: Path) -> Path:
        """Validate output file path.

        Args:
            v: Output file path

        Returns:
            Validated and resolved Path object

        Raises:
            ValueError: If parent directory doesn't exist or path is invalid
        """
        resolved = v.resolve()
        if not resolved.parent.exists():
            raise ValueError(f"Output file parent directory does not exist: {resolved.parent}")
        if resolved.exists() and resolved.is_dir():
            raise ValueError(f"Output path is a directory, not a file: {resolved}")
        return resolved

    @field_validator("config_file")
    @classmethod
    def validate_config_file(cls, v: Path | None) -> Path | None:
        """Validate configuration file if provided.

        Args:
            v: Configuration file path

        Returns:
            Validated and resolved Path object or None

        Raises:
            ValueError: If config file doesn't exist or isn't readable
        """
        if v is None:
            return None
        resolved = v.resolve()
        if not resolved.exists():
            raise ValueError(f"Configuration file does not exist: {resolved}")
        if not resolved.is_file():
            raise ValueError(f"Configuration path is not a file: {resolved}")
        return resolved
