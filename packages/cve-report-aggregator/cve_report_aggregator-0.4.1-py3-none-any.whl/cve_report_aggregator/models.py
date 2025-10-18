"""Data models and type definitions for CVE report aggregation."""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator

# Type aliases for better type hints
ScannerType = Literal["grype", "trivy"]
ModeType = Literal["highest-score", "first-occurrence", "grype-only", "trivy-only"]


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


class AggregatorConfig(BaseModel):
    """Configuration model for CVE Report Aggregator.

    This model provides comprehensive validation of all configuration
    parameters including paths, scanner selection, and operational modes.

    Attributes:
        input_dir: Directory containing scan report files
        output_file: Path for the unified output report
        scanner: Scanner type to use (grype or trivy)
        mode: Aggregation mode for vulnerability processing
        verbose: Enable detailed logging output
        config_file: Optional path to YAML configuration file
        registry: Container registry URL
        organization: Organization or namespace in the registry
        packages: List of packages to scan
    """

    input_dir: Path = Field(
        default=Path.cwd() / "reports",
        description="Input directory containing scan report files",
    )
    output_file: Path = Field(
        default=Path.cwd() / "unified-report.json",
        description="Output file path for the unified report",
    )
    scanner: ScannerType = Field(
        default="grype",
        description="Vulnerability scanner to use",
    )
    mode: ModeType = Field(
        default="highest-score",
        description="Aggregation mode for vulnerability processing",
    )
    verbose: bool = Field(
        default=False,
        description="Enable verbose output with detailed processing information",
    )
    config_file: Path | None = Field(
        default=None,
        description="Path to YAML configuration file",
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

    class Config:
        """Pydantic configuration."""

        validate_assignment = True
        frozen = False

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
