"""Tests for configuration management module using Pydantic Settings."""

from pathlib import Path

import pytest

from cve_report_aggregator.config import (
    AggregatorSettings,
    get_config,
    load_settings,
)
from cve_report_aggregator.models import AggregatorConfig, PackageConfig


@pytest.fixture
def create_example_config():
    """Fixture to create example YAML configuration files for testing."""

    def _create_config(output_path: Path) -> None:
        """Create an example YAML configuration file.

        Args:
            output_path: Path where to write the example config
        """
        example_config = """# CVE Report Aggregator Configuration
# This file can be placed at:
#   - ./.cve-aggregator.yaml (current directory - auto-discovered)
#   - ./.cve-aggregator.yml (current directory - auto-discovered)
# Or specify explicitly with --config flag

# Input directory containing scan report files
input_dir: ./reports

# Output file path for the unified report
output_file: ./unified-report.json

# Scanner type: grype or trivy
scanner: grype

# Aggregation mode:
#   - highest-score: Select highest CVSS 3.x score across all reports
#   - first-occurrence: Use severity from first occurrence
#   - grype-only: Process only with Grype scanner
#   - trivy-only: Process only with Trivy scanner
mode: highest-score

# Enable verbose output
verbose: false
"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(example_config)

    return _create_config


class TestAggregatorSettings:
    """Tests for AggregatorSettings class."""

    def test_default_settings(self):
        """Test that default settings are properly initialized."""
        settings = AggregatorSettings()

        assert settings.input_dir == Path.cwd() / "reports"
        assert settings.output_file == Path.cwd() / "unified-report.json"
        assert settings.scanner == "grype"
        assert settings.mode == "highest-score"
        assert settings.verbose is False
        assert settings.config_file is None

    def test_settings_from_dict(self, tmp_path):
        """Test creating settings from dictionary."""
        input_dir = tmp_path / "custom-reports"
        input_dir.mkdir()

        settings = AggregatorSettings(
            input_dir=input_dir,
            scanner="trivy",
            mode="first-occurrence",
            verbose=True,
        )

        assert settings.input_dir == input_dir
        assert settings.scanner == "trivy"
        assert settings.mode == "first-occurrence"
        assert settings.verbose is True

    def test_settings_with_env_vars(self, monkeypatch, tmp_path):
        """Test loading settings from environment variables."""
        input_dir = tmp_path / "env-reports"
        input_dir.mkdir()

        monkeypatch.setenv("CVE_AGGREGATOR_INPUT_DIR", str(input_dir))
        monkeypatch.setenv("CVE_AGGREGATOR_SCANNER", "trivy")
        monkeypatch.setenv("CVE_AGGREGATOR_VERBOSE", "true")

        settings = AggregatorSettings()

        assert settings.input_dir == input_dir
        assert settings.scanner == "trivy"
        assert settings.verbose is True

    def test_to_aggregator_config(self, tmp_path):
        """Test converting settings to AggregatorConfig."""
        input_dir = tmp_path / "reports"
        input_dir.mkdir()

        settings = AggregatorSettings(input_dir=input_dir)
        config = settings.to_aggregator_config()

        assert isinstance(config, AggregatorConfig)
        assert config.input_dir == input_dir


class TestYamlConfigLoading:
    """Tests for YAML configuration file loading using YamlConfigSettingsSource."""

    def test_load_from_yaml_file(self, tmp_path, monkeypatch):
        """Test loading configuration from YAML file."""
        # Change to temp directory for test isolation
        monkeypatch.chdir(tmp_path)

        input_dir = tmp_path / "yaml-reports"
        input_dir.mkdir()

        # Create .cve-aggregator.yaml in current directory
        config_file = tmp_path / ".cve-aggregator.yaml"
        config_file.write_text(
            f"""
input_dir: {input_dir}
scanner: trivy
mode: first-occurrence
verbose: true
"""
        )

        # Settings should auto-discover the config file
        settings = AggregatorSettings()

        assert settings.input_dir == input_dir
        assert settings.scanner == "trivy"
        assert settings.mode == "first-occurrence"
        assert settings.verbose is True

    def test_load_from_yml_extension(self, tmp_path, monkeypatch):
        """Test loading from .yml extension."""
        monkeypatch.chdir(tmp_path)

        # Create .cve-aggregator.yml
        config_file = tmp_path / ".cve-aggregator.yml"
        config_file.write_text(
            """
scanner: trivy
verbose: true
"""
        )

        settings = AggregatorSettings()

        assert settings.scanner == "trivy"
        assert settings.verbose is True

    def test_yaml_file_priority_over_defaults(self, tmp_path, monkeypatch):
        """Test that YAML file takes priority over defaults."""
        monkeypatch.chdir(tmp_path)

        config_file = tmp_path / ".cve-aggregator.yaml"
        config_file.write_text(
            """
scanner: trivy
mode: grype-only
"""
        )

        settings = AggregatorSettings()

        # YAML values override defaults
        assert settings.scanner == "trivy"
        assert settings.mode == "grype-only"
        # Defaults still work for unspecified values
        assert settings.verbose is False


class TestLoadSettings:
    """Tests for load_settings function."""

    def test_load_with_defaults(self):
        """Test loading with default values."""
        settings = load_settings()

        assert settings.input_dir == Path.cwd() / "reports"
        assert settings.scanner == "grype"
        assert settings.verbose is False

    def test_load_with_cli_args(self, tmp_path):
        """Test loading with CLI arguments."""
        input_dir = tmp_path / "cli-reports"
        input_dir.mkdir()

        cli_args = {
            "input_dir": input_dir,
            "scanner": "trivy",
            "verbose": True,
        }

        settings = load_settings(cli_args=cli_args)

        assert settings.input_dir == input_dir
        assert settings.scanner == "trivy"
        assert settings.verbose is True

    def test_load_with_explicit_config_file(self, tmp_path):
        """Test loading with explicit config file path."""
        input_dir = tmp_path / "explicit-reports"
        input_dir.mkdir()

        config_file = tmp_path / "my-config.yaml"
        config_file.write_text(
            f"""
input_dir: {input_dir}
scanner: trivy
mode: trivy-only
"""
        )

        settings = load_settings(config_file_path=config_file)

        assert settings.input_dir == input_dir
        assert settings.scanner == "trivy"
        assert settings.mode == "trivy-only"
        assert settings.config_file == config_file

    def test_cli_overrides_yaml(self, tmp_path):
        """Test that CLI arguments override YAML config."""
        input_dir = tmp_path / "override-reports"
        input_dir.mkdir()

        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            """
scanner: trivy
verbose: false
"""
        )

        cli_args = {
            "scanner": "grype",  # Override YAML
            "verbose": True,  # Override YAML
        }

        settings = load_settings(cli_args=cli_args, config_file_path=config_file)

        # CLI args take precedence
        assert settings.scanner == "grype"
        assert settings.verbose is True

    def test_cli_none_values_dont_override(self, tmp_path):
        """Test that None CLI values don't override config values."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            """
scanner: trivy
verbose: true
"""
        )

        cli_args = {
            "scanner": None,  # Should not override
            "verbose": None,  # Should not override
        }

        settings = load_settings(cli_args=cli_args, config_file_path=config_file)

        # YAML values should be preserved
        assert settings.scanner == "trivy"
        assert settings.verbose is True

    def test_load_with_env_vars(self, monkeypatch, tmp_path):
        """Test that environment variables are loaded."""
        input_dir = tmp_path / "env-reports"
        input_dir.mkdir()

        monkeypatch.setenv("CVE_AGGREGATOR_INPUT_DIR", str(input_dir))
        monkeypatch.setenv("CVE_AGGREGATOR_SCANNER", "trivy")

        settings = load_settings()

        assert settings.input_dir == input_dir
        assert settings.scanner == "trivy"


class TestGetConfig:
    """Tests for get_config function."""

    def test_get_config_with_valid_args(self, tmp_path):
        """Test getting config with valid arguments."""
        input_dir = tmp_path / "reports"
        input_dir.mkdir()

        cli_args = {
            "input_dir": input_dir,
            "output_file": tmp_path / "output.json",
        }

        config = get_config(cli_args=cli_args)

        assert isinstance(config, AggregatorConfig)
        assert config.input_dir == input_dir

    def test_get_config_with_yaml(self, tmp_path):
        """Test getting config from YAML file."""
        input_dir = tmp_path / "yaml-reports"
        input_dir.mkdir()

        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            f"""
input_dir: {input_dir}
scanner: trivy
"""
        )

        config = get_config(config_file_path=config_file)

        assert isinstance(config, AggregatorConfig)
        assert config.input_dir == input_dir
        assert config.scanner == "trivy"

    def test_get_config_priority_order(self, tmp_path, monkeypatch):
        """Test configuration priority order."""
        input_dir_cli = tmp_path / "cli-reports"
        input_dir_cli.mkdir()

        input_dir_yaml = tmp_path / "yaml-reports"
        input_dir_yaml.mkdir()

        # Set environment variable (lowest priority)
        monkeypatch.setenv("CVE_AGGREGATOR_VERBOSE", "false")

        # Create YAML config (higher priority)
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            f"""
input_dir: {input_dir_yaml}
scanner: trivy
verbose: true
"""
        )

        # CLI args (highest priority)
        cli_args = {
            "input_dir": input_dir_cli,
        }

        config = get_config(cli_args=cli_args, config_file_path=config_file)

        # CLI takes precedence for input_dir
        assert config.input_dir == input_dir_cli
        # YAML value used for scanner (not in CLI)
        assert config.scanner == "trivy"
        # YAML takes precedence for verbose (over env var)
        assert config.verbose is True


class TestRegistryAndPackages:
    """Tests for registry and packages configuration."""

    def test_registry_and_packages_from_yaml(self, tmp_path, monkeypatch):
        """Test loading registry and packages from YAML."""
        monkeypatch.chdir(tmp_path)

        config_file = tmp_path / ".cve-aggregator.yaml"
        config_file.write_text(
            """
registry: registry.defenseunicorns.com
organization: sld-45
packages:
  - name: gitlab
    version: 18.4.2-uds.0-unicorn
    architecture: amd64
  - name: gitlab-runner
    version: 18.4.0-uds.0-unicorn
    architecture: amd64
  - name: headlamp
    version: 0.35.0-uds.0-registry1
    architecture: amd64
"""
        )

        settings = AggregatorSettings()

        assert settings.registry == "registry.defenseunicorns.com"
        assert settings.organization == "sld-45"
        assert len(settings.packages) == 3
        assert settings.packages[0].name == "gitlab"
        assert settings.packages[0].version == "18.4.2-uds.0-unicorn"
        assert settings.packages[0].architecture == "amd64"
        assert settings.packages[1].name == "gitlab-runner"
        assert settings.packages[2].name == "headlamp"

    def test_packages_default_architecture(self, tmp_path, monkeypatch):
        """Test that packages use default architecture if not specified."""
        monkeypatch.chdir(tmp_path)

        config_file = tmp_path / ".cve-aggregator.yaml"
        config_file.write_text(
            """
packages:
  - name: test-package
    version: 1.0.0
"""
        )

        settings = AggregatorSettings()

        assert len(settings.packages) == 1
        assert settings.packages[0].architecture == "amd64"

    def test_to_aggregator_config_with_packages(self, tmp_path):
        """Test converting settings with packages to AggregatorConfig."""
        input_dir = tmp_path / "reports"
        input_dir.mkdir()

        packages = [
            PackageConfig(name="gitlab", version="18.4.2", architecture="amd64"),
            PackageConfig(name="gitlab-runner", version="18.4.0", architecture="arm64"),
        ]

        settings = AggregatorSettings(
            input_dir=input_dir,
            registry="registry.example.com",
            organization="test-org",
            packages=packages,
        )

        config = settings.to_aggregator_config()

        assert isinstance(config, AggregatorConfig)
        assert config.registry == "registry.example.com"
        assert config.organization == "test-org"
        assert len(config.packages) == 2
        assert config.packages[0].name == "gitlab"
        assert config.packages[1].architecture == "arm64"

    def test_empty_packages_list(self, tmp_path):
        """Test that empty packages list is handled correctly."""
        input_dir = tmp_path / "reports"
        input_dir.mkdir()

        settings = AggregatorSettings(input_dir=input_dir)

        assert settings.packages == []
        assert settings.registry is None
        assert settings.organization is None


class TestCreateExampleConfig:
    """Tests for create_example_config fixture."""

    def test_create_example_config(self, tmp_path, create_example_config):
        """Test creating example configuration file."""
        output_path = tmp_path / ".cve-aggregator.yaml"

        create_example_config(output_path)

        assert output_path.exists()
        content = output_path.read_text()
        assert "CVE Report Aggregator Configuration" in content
        assert "input_dir:" in content
        assert "scanner:" in content

    def test_create_example_config_creates_parent_dirs(self, tmp_path, create_example_config):
        """Test that parent directories are created if needed."""
        output_path = tmp_path / "config" / "subdir" / ".cve-aggregator.yaml"

        create_example_config(output_path)

        assert output_path.exists()
        assert output_path.parent.exists()

    def test_example_config_is_valid_yaml(self, tmp_path, create_example_config):
        """Test that generated example config is valid YAML."""
        import yaml

        output_path = tmp_path / ".cve-aggregator.yaml"
        create_example_config(output_path)

        # Should be parseable as YAML (comments are ignored)
        content = output_path.read_text()
        # Remove comment-only lines for YAML parsing
        yaml_lines = [line for line in content.split("\n") if line.strip() and not line.strip().startswith("#")]
        yaml_content = "\n".join(yaml_lines)

        # Should parse without errors
        parsed = yaml.safe_load(yaml_content)
        assert isinstance(parsed, dict)
