"""Configuration management using Pydantic Settings with YAML support.

This module provides a comprehensive configuration system that supports:
- CLI arguments (highest priority)
- YAML configuration files
- Environment variables
- Default values (lowest priority)

Configuration precedence (from highest to lowest):
1. CLI arguments
2. YAML configuration file
3. Environment variables
4. Default values
"""

from pathlib import Path
from typing import Any

from pydantic import ValidationInfo, field_validator
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict, YamlConfigSettingsSource

from .models import AggregatorConfig, ModeType, PackageConfig, ScannerType


class AggregatorSettings(BaseSettings):
    """Application settings with support for multiple configuration sources.

    This class extends Pydantic Settings to provide:
    - Environment variable loading with CVE_AGGREGATOR_ prefix
    - YAML file configuration support via YamlConfigSettingsSource
    - Type validation and coercion
    - Configuration merging with proper precedence

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

    input_dir: Path = Path.cwd() / "reports"
    output_file: Path = Path.cwd() / "unified-report.json"
    scanner: ScannerType = "grype"
    mode: ModeType = "highest-score"
    verbose: bool = False
    config_file: Path | None = None
    registry: str | None = None
    organization: str | None = None
    packages: list[PackageConfig] = []

    model_config = SettingsConfigDict(
        env_prefix="CVE_AGGREGATOR_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        validate_assignment=True,
        extra="ignore",
        yaml_file=[".cve-aggregator.yaml", ".cve-aggregator.yml"],
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Customize settings sources and their priority order.

        Priority order (highest to lowest):
        1. init_settings - Values passed to __init__ (CLI args)
        2. yaml_settings - YAML configuration file
        3. env_settings - Environment variables
        4. dotenv_settings - .env file
        5. file_secret_settings - Secret files

        Returns:
            Tuple of settings sources in priority order
        """
        return (
            init_settings,
            YamlConfigSettingsSource(settings_cls),
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

    @field_validator("input_dir", "output_file", mode="before")
    @classmethod
    def convert_str_to_path(cls, v: Any, info: ValidationInfo) -> Path:
        """Convert string paths to Path objects.

        Args:
            v: Value to convert
            info: Validation context

        Returns:
            Path object
        """
        if isinstance(v, str):
            return Path(v)
        if isinstance(v, Path):
            return v
        # If it's neither str nor Path, let Pydantic handle validation
        return Path(v)

    def to_aggregator_config(self) -> AggregatorConfig:
        """Convert settings to validated AggregatorConfig.

        Returns:
            Validated AggregatorConfig instance

        Raises:
            ValidationError: If configuration validation fails
        """
        return AggregatorConfig(
            input_dir=self.input_dir,
            output_file=self.output_file,
            scanner=self.scanner,
            mode=self.mode,
            verbose=self.verbose,
            config_file=self.config_file,
            registry=self.registry,
            organization=self.organization,
            packages=self.packages,
        )


def load_settings(
    cli_args: dict[str, Any] | None = None,
    config_file_path: Path | None = None,
) -> AggregatorSettings:
    """Load settings from all sources with proper precedence.

    This function uses Pydantic Settings with YamlConfigSettingsSource to handle
    configuration loading. The precedence order is managed by settings_customise_sources.

    Configuration precedence (from highest to lowest):
    1. CLI arguments (cli_args parameter)
    2. Explicit config file (config_file_path parameter) OR auto-discovered YAML
    3. Environment variables
    4. Default values

    Args:
        cli_args: Dictionary of CLI arguments (highest priority)
        config_file_path: Explicit path to configuration file (overrides yaml_file)

    Returns:
        Loaded and validated settings

    Raises:
        ValidationError: If configuration validation fails

    Examples:
        >>> # Load with defaults and environment variables
        >>> settings = load_settings()

        >>> # Load with CLI arguments
        >>> settings = load_settings(cli_args={'verbose': True})

        >>> # Load with explicit config file
        >>> settings = load_settings(config_file_path=Path('./my-config.yaml'))
    """
    # Filter out None values from CLI args to avoid overriding valid config values
    filtered_cli_args = {k: v for k, v in (cli_args or {}).items() if v is not None}

    # If explicit config file provided, create a custom settings class with that file
    if config_file_path:
        # Create a custom settings class with the explicit config file
        class CustomSettings(AggregatorSettings):
            model_config = SettingsConfigDict(
                env_prefix="CVE_AGGREGATOR_",
                env_file=".env",
                env_file_encoding="utf-8",
                case_sensitive=False,
                validate_assignment=True,
                extra="ignore",
                yaml_file=str(config_file_path),
            )

        settings: AggregatorSettings = CustomSettings(**filtered_cli_args)
        # Store the config file path for reference
        settings.config_file = config_file_path
    else:
        # Use default settings with auto-discovery
        settings = AggregatorSettings(**filtered_cli_args)

    return settings


def get_config(
    cli_args: dict[str, Any] | None = None,
    config_file_path: Path | None = None,
) -> AggregatorConfig:
    """Load and validate complete configuration.

    This is the main entry point for configuration loading. It handles:
    - Loading from all configuration sources
    - Merging with proper precedence
    - Full validation of final configuration

    Args:
        cli_args: Dictionary of CLI arguments
        config_file_path: Optional path to configuration file

    Returns:
        Fully validated AggregatorConfig instance

    Raises:
        ValidationError: If configuration validation fails
        FileNotFoundError: If specified config file doesn't exist
        ValueError: If config file is invalid

    Examples:
        >>> # Load with CLI arguments
        >>> config = get_config(cli_args={'input_dir': Path('./reports'), 'verbose': True})
        >>> print(config.verbose)
        True

        >>> # Load with config file
        >>> config = get_config(config_file_path=Path('./config.yaml'))

        >>> # Load with both (CLI takes precedence)
        >>> config = get_config(
        ...     cli_args={'verbose': True},
        ...     config_file_path=Path('./config.yaml')
        ... )
    """
    settings = load_settings(cli_args=cli_args, config_file_path=config_file_path)
    return settings.to_aggregator_config()
