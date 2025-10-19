"""Comprehensive tests for the downloader module.

This test suite validates the package SBOM downloading functionality
including command execution, file operations, error handling, and cleanup.
"""

from unittest.mock import patch

import pytest

from cve_report_aggregator.core.config import config_context
from cve_report_aggregator.core.models import AggregatorConfig, PackageConfig
from cve_report_aggregator.io.downloader import download_package_sbom, download_package_sboms


@pytest.fixture
def mock_config(tmp_path):
    """Create a mock configuration for testing."""
    input_dir = tmp_path / "reports"
    input_dir.mkdir()

    return AggregatorConfig(
        input_dir=input_dir,
        output_file=tmp_path / "output.json",
        scanner="grype",
        mode="highest-score",
        verbose=False,
        downloadRemotePackages=True,
        registry="registry.example.com",
        organization="test-org",
        packages=[
            PackageConfig(name="test-package", version="1.0.0", architecture="amd64"),
        ],
    )


@pytest.fixture
def mock_config_verbose(tmp_path):
    """Create a mock configuration with verbose enabled."""
    input_dir = tmp_path / "reports"
    input_dir.mkdir()

    return AggregatorConfig(
        input_dir=input_dir,
        output_file=tmp_path / "output.json",
        scanner="grype",
        mode="highest-score",
        verbose=True,
        downloadRemotePackages=True,
        registry="registry.example.com",
        organization="test-org",
        packages=[
            PackageConfig(name="test-package", version="1.0.0", architecture="amd64"),
        ],
    )


@pytest.fixture
def mock_config_no_download(tmp_path):
    """Create a mock configuration with downloadRemotePackages=False."""
    input_dir = tmp_path / "reports"
    input_dir.mkdir()

    return AggregatorConfig(
        input_dir=input_dir,
        output_file=tmp_path / "output.json",
        scanner="grype",
        mode="highest-score",
        verbose=False,
        downloadRemotePackages=False,
    )


@pytest.fixture
def sample_package():
    """Create a sample package configuration."""
    return PackageConfig(name="gitlab", version="18.4.2-uds.0-unicorn", architecture="amd64")


@pytest.fixture
def sample_packages():
    """Create multiple sample package configurations."""
    return [
        PackageConfig(name="gitlab", version="18.4.2-uds.0-unicorn", architecture="amd64"),
        PackageConfig(name="gitlab-runner", version="18.4.0-uds.0-unicorn", architecture="amd64"),
        PackageConfig(name="headlamp", version="0.35.0-uds.0-registry1", architecture="arm64"),
    ]


class TestDownloadPackageSboms:
    """Tests for download_package_sboms function."""

    def test_download_disabled_returns_empty_list(self, mock_config_no_download):
        """Test that downloadRemotePackages=False returns empty list early."""
        with config_context(mock_config_no_download):
            with patch("cve_report_aggregator.io.downloader.download_package_sbom") as mock_download:
                output_dir = mock_config_no_download.input_dir
                result = download_package_sboms(output_dir)

                assert result == []
                mock_download.assert_not_called()

    def test_missing_registry_raises_error(self, tmp_path):
        """Test that missing registry raises ValueError."""
        input_dir = tmp_path / "reports"
        input_dir.mkdir()

        config = AggregatorConfig(
            input_dir=input_dir,
            output_file=tmp_path / "output.json",
            downloadRemotePackages=True,
            registry=None,  # Missing registry
            organization="test-org",
            packages=[PackageConfig(name="test", version="1.0.0", architecture="amd64")],
        )

        with config_context(config):
            with pytest.raises(ValueError, match="Registry URL is required"):
                download_package_sboms(tmp_path / "output")

    def test_missing_organization_raises_error(self, tmp_path):
        """Test that missing organization raises ValueError."""
        input_dir = tmp_path / "reports"
        input_dir.mkdir()

        config = AggregatorConfig(
            input_dir=input_dir,
            output_file=tmp_path / "output.json",
            downloadRemotePackages=True,
            registry="registry.example.com",
            organization=None,  # Missing organization
            packages=[PackageConfig(name="test", version="1.0.0", architecture="amd64")],
        )

        with config_context(config):
            with pytest.raises(ValueError, match="Organization is required"):
                download_package_sboms(tmp_path / "output")

    def test_no_packages_configured_returns_empty_list(self, tmp_path):
        """Test that no packages configured returns empty list with warning."""
        input_dir = tmp_path / "reports"
        input_dir.mkdir()

        config = AggregatorConfig(
            input_dir=input_dir,
            output_file=tmp_path / "output.json",
            downloadRemotePackages=True,
            registry="registry.example.com",
            organization="test-org",
            packages=[],  # No packages
        )

        with config_context(config):
            output_dir = tmp_path / "output"
            result = download_package_sboms(output_dir)

            assert result == []

    def test_successful_single_package_download(self, mock_config, tmp_path):
        """Test successful download of a single package."""
        with config_context(mock_config):
            output_dir = tmp_path / "output"
            output_dir.mkdir()

            # Create fake SBOM files that would be returned
            fake_sbom = output_dir / "test-package-1.0.0-sbom.json"
            fake_sbom.write_text('{"test": "data"}')

            with patch("cve_report_aggregator.io.downloader.download_package_sbom") as mock_download:
                mock_download.return_value = [fake_sbom]

                result = download_package_sboms(output_dir)

                assert len(result) == 1
                assert result[0] == fake_sbom
                mock_download.assert_called_once()

    def test_successful_multiple_packages_download(self, tmp_path, sample_packages):
        """Test successful download of multiple packages."""
        input_dir = tmp_path / "reports"
        input_dir.mkdir()

        config = AggregatorConfig(
            input_dir=input_dir,
            output_file=tmp_path / "output.json",
            downloadRemotePackages=True,
            registry="registry.example.com",
            organization="test-org",
            packages=sample_packages,
            verbose=False,
        )

        with config_context(config):
            output_dir = tmp_path / "output"
            output_dir.mkdir()

            # Create fake SBOM files for each package
            fake_sboms = [output_dir / f"{pkg.name}-{pkg.version}-sbom.json" for pkg in sample_packages]
            for sbom in fake_sboms:
                sbom.write_text('{"test": "data"}')

            with patch("cve_report_aggregator.io.downloader.download_package_sbom") as mock_download:
                mock_download.side_effect = [[sbom] for sbom in fake_sboms]

                result = download_package_sboms(output_dir)

                assert len(result) == 3
                assert all(sbom in result for sbom in fake_sboms)
                assert mock_download.call_count == 3

    def test_partial_failure_continues_with_others(self, tmp_path, sample_packages):
        """Test that failure of one package doesn't stop others."""
        input_dir = tmp_path / "reports"
        input_dir.mkdir()

        config = AggregatorConfig(
            input_dir=input_dir,
            output_file=tmp_path / "output.json",
            downloadRemotePackages=True,
            registry="registry.example.com",
            organization="test-org",
            packages=sample_packages,
            verbose=False,
        )

        with config_context(config):
            output_dir = tmp_path / "output"
            output_dir.mkdir()

            # Create fake SBOM files for successful packages
            successful_sboms = [
                output_dir / f"{sample_packages[0].name}-sbom.json",
                output_dir / f"{sample_packages[2].name}-sbom.json",
            ]
            for sbom in successful_sboms:
                sbom.write_text('{"test": "data"}')

            with patch("cve_report_aggregator.io.downloader.download_package_sbom") as mock_download:
                # First succeeds, second fails, third succeeds
                mock_download.side_effect = [
                    [successful_sboms[0]],
                    RuntimeError("Download failed"),
                    [successful_sboms[1]],
                ]

                result = download_package_sboms(output_dir)

                # Should have 2 successful downloads despite 1 failure
                assert len(result) == 2
                assert successful_sboms[0] in result
                assert successful_sboms[1] in result
                assert mock_download.call_count == 3

    def test_creates_output_directory_if_not_exists(self, mock_config, tmp_path):
        """Test that output directory is created if it doesn't exist."""
        with config_context(mock_config):
            output_dir = tmp_path / "new_output_dir"
            assert not output_dir.exists()

            with patch("cve_report_aggregator.io.downloader.download_package_sbom") as mock_download:
                mock_download.return_value = []

                download_package_sboms(output_dir)

                assert output_dir.exists()
                assert output_dir.is_dir()

    def test_verbose_output(self, mock_config_verbose, tmp_path):
        """Test verbose output during downloads."""
        with config_context(mock_config_verbose):
            output_dir = tmp_path / "output"
            output_dir.mkdir()

            fake_sbom = output_dir / "test-package-sbom.json"
            fake_sbom.write_text('{"test": "data"}')

            with patch("cve_report_aggregator.io.downloader.download_package_sbom") as mock_download:
                mock_download.return_value = [fake_sbom]

                with patch("cve_report_aggregator.io.downloader.console") as mock_console:
                    download_package_sboms(output_dir)

                    # Verify verbose console output was called
                    assert mock_console.print.call_count >= 2
                    # Check for initial message
                    call_args_list = [str(call_obj) for call_obj in mock_console.print.call_args_list]
                    assert any("Downloading SBOM reports" in str(call_obj) for call_obj in call_args_list)

    def test_verbose_output_on_error(self, tmp_path, sample_packages):
        """Test verbose error output when download fails."""
        input_dir = tmp_path / "reports"
        input_dir.mkdir()

        config = AggregatorConfig(
            input_dir=input_dir,
            output_file=tmp_path / "output.json",
            downloadRemotePackages=True,
            registry="registry.example.com",
            organization="test-org",
            packages=sample_packages[:1],  # Just one package
            verbose=True,
        )

        with config_context(config):
            output_dir = tmp_path / "output"

            with patch("cve_report_aggregator.io.downloader.download_package_sbom") as mock_download:
                mock_download.side_effect = RuntimeError("Download failed")

                with patch("cve_report_aggregator.io.downloader.console") as mock_console:
                    result = download_package_sboms(output_dir)

                    # Should show error message
                    call_args_list = [str(call_obj) for call_obj in mock_console.print.call_args_list]
                    assert any("✗" in str(call_obj) or "Failed" in str(call_obj) for call_obj in call_args_list)

                    assert result == []


class TestDownloadPackageSbom:
    """Tests for download_package_sbom function."""

    def test_successful_download_with_sbom_files(self, sample_package, tmp_path, mock_config):
        """Test successful download with SBOM files found."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create a temp directory structure that mktemp would create
        temp_dir = tmp_path / "temp_sbom_123"
        temp_dir.mkdir()

        # Create package subdirectory with JSON files
        package_temp_dir = temp_dir / f"{sample_package.name}-sbom"
        package_temp_dir.mkdir()

        # Create sample SBOM files
        (package_temp_dir / "sbom.json").write_text('{"test": "sbom1"}')
        (package_temp_dir / "sbom-layer.json").write_text('{"test": "sbom2"}')

        with config_context(mock_config):
            with patch("cve_report_aggregator.core.executor.ExecutorManager.create_temp_directory") as mock_mktemp:
                with patch("cve_report_aggregator.core.executor.ExecutorManager.execute") as mock_execute:
                    # Mock create_temp_directory to return our temp directory
                    mock_mktemp.return_value = (temp_dir, None)
                    # Mock uds command to succeed
                    mock_execute.return_value = ("", None)

                    result = download_package_sbom(
                        package=sample_package,
                        registry="registry.example.com",
                        organization="test-org",
                        output_dir=output_dir,
                        verbose=False,
                    )

                    # Should have copied both JSON files
                    assert len(result) == 2
                    assert all(f.exists() for f in result)
                    assert all(f.parent == output_dir for f in result)

                    # Verify command calls
                    mock_mktemp.assert_called_once()
                    mock_execute.assert_called_once()
                    # Verify uds command
                    uds_call = mock_execute.call_args[0][0]
                    assert uds_call[0] == "uds"
                    assert uds_call[1] == "zarf"
                    assert uds_call[2] == "package"
                    assert uds_call[3] == "inspect"
                    assert uds_call[4] == "sbom"
                    assert "registry.example.com/test-org/gitlab-18.4.2-uds.0-unicorn" in uds_call[5]
                    assert "-a" in uds_call
                    assert "amd64" in uds_call
                    assert "--output" in uds_call

    def test_no_sbom_files_found(self, sample_package, tmp_path, mock_config):
        """Test when no SBOM files are found in downloaded directory."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create a temp directory structure without JSON files
        temp_dir = tmp_path / "temp_sbom_456"
        temp_dir.mkdir()

        package_temp_dir = temp_dir / f"{sample_package.name}-sbom"
        package_temp_dir.mkdir()
        # No JSON files created

        with config_context(mock_config):
            with patch("cve_report_aggregator.core.executor.ExecutorManager.create_temp_directory") as mock_mktemp:
                with patch("cve_report_aggregator.core.executor.ExecutorManager.execute") as mock_execute:
                    mock_mktemp.return_value = (temp_dir, None)
                    mock_execute.return_value = ("", None)

                    result = download_package_sbom(
                        package=sample_package,
                        registry="registry.example.com",
                        organization="test-org",
                        output_dir=output_dir,
                        verbose=False,
                    )

                    # Should return empty list
                    assert result == []

    def test_package_directory_not_created(self, sample_package, tmp_path, mock_config):
        """Test when uds command doesn't create the expected directory."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create a temp directory but NOT the package subdirectory
        temp_dir = tmp_path / "temp_sbom_no_pkg_dir"
        temp_dir.mkdir()
        # package_temp_dir is NOT created - simulating uds command not creating it

        with config_context(mock_config):
            with patch("cve_report_aggregator.core.executor.ExecutorManager.create_temp_directory") as mock_mktemp:
                with patch("cve_report_aggregator.core.executor.ExecutorManager.execute") as mock_execute:
                    mock_mktemp.return_value = (temp_dir, None)
                    mock_execute.return_value = ("", None)

                    result = download_package_sbom(
                        package=sample_package,
                        registry="registry.example.com",
                        organization="test-org",
                        output_dir=output_dir,
                        verbose=False,
                    )

                    # Should return empty list because package_temp_dir doesn't exist
                    assert result == []

    def test_missing_package_name_raises_error(self, tmp_path, mock_config):
        """Test that missing package name raises ValueError."""
        invalid_package = PackageConfig(name="", version="1.0.0", architecture="amd64")

        output_dir = tmp_path / "output"

        with config_context(mock_config):
            with pytest.raises(ValueError, match="Package name is required"):
                download_package_sbom(
                    package=invalid_package,
                    registry="registry.example.com",
                    organization="test-org",
                    output_dir=output_dir,
                )

    def test_missing_package_version_raises_error(self, tmp_path, mock_config):
        """Test that missing package version raises ValueError."""
        invalid_package = PackageConfig(name="test", version="", architecture="amd64")

        output_dir = tmp_path / "output"

        with config_context(mock_config):
            with pytest.raises(ValueError, match="Package version is required"):
                download_package_sbom(
                    package=invalid_package,
                    registry="registry.example.com",
                    organization="test-org",
                    output_dir=output_dir,
                )

    def test_missing_package_architecture_raises_error(self, tmp_path, mock_config):
        """Test that missing package architecture raises ValueError."""
        invalid_package = PackageConfig(name="test", version="1.0.0", architecture="")

        output_dir = tmp_path / "output"

        with config_context(mock_config):
            with pytest.raises(ValueError, match="Package architecture is required"):
                download_package_sbom(
                    package=invalid_package,
                    registry="registry.example.com",
                    organization="test-org",
                    output_dir=output_dir,
                )

    def test_mktemp_command_failure(self, sample_package, tmp_path, mock_config):
        """Test that mktemp command failure raises RuntimeError."""
        output_dir = tmp_path / "output"

        with config_context(mock_config):
            with patch("cve_report_aggregator.core.executor.ExecutorManager.create_temp_directory") as mock_mktemp:
                # mktemp fails
                mock_mktemp.return_value = (tmp_path / "nonexistent", RuntimeError("mktemp failed"))

                with pytest.raises(RuntimeError, match="Failed to create temporary directory"):
                    download_package_sbom(
                        package=sample_package,
                        registry="registry.example.com",
                        organization="test-org",
                        output_dir=output_dir,
                    )

    def test_uds_command_failure(self, sample_package, tmp_path, mock_config):
        """Test that uds command failure raises RuntimeError."""
        output_dir = tmp_path / "output"

        temp_dir = tmp_path / "temp_sbom_789"
        temp_dir.mkdir()

        with config_context(mock_config):
            with patch("cve_report_aggregator.core.executor.ExecutorManager.create_temp_directory") as mock_mktemp:
                with patch("cve_report_aggregator.core.executor.ExecutorManager.execute") as mock_execute:
                    # mktemp succeeds, uds fails
                    mock_mktemp.return_value = (temp_dir, None)
                    mock_execute.return_value = ("", RuntimeError("uds command failed"))

                    with pytest.raises(RuntimeError, match="Failed to download SBOM"):
                        download_package_sbom(
                            package=sample_package,
                            registry="registry.example.com",
                            organization="test-org",
                            output_dir=output_dir,
                        )

    def test_temporary_directory_cleanup_on_success(self, sample_package, tmp_path, mock_config):
        """Test that temporary directory is cleaned up after success."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        temp_dir = tmp_path / "temp_sbom_cleanup"
        temp_dir.mkdir()

        package_temp_dir = temp_dir / f"{sample_package.name}-sbom"
        package_temp_dir.mkdir()
        (package_temp_dir / "sbom.json").write_text('{"test": "data"}')

        with config_context(mock_config):
            with patch("cve_report_aggregator.core.executor.ExecutorManager.create_temp_directory") as mock_mktemp:
                with patch("cve_report_aggregator.core.executor.ExecutorManager.execute") as mock_execute:
                    mock_mktemp.return_value = (temp_dir, None)
                    mock_execute.return_value = ("", None)

                    download_package_sbom(
                        package=sample_package,
                        registry="registry.example.com",
                        organization="test-org",
                        output_dir=output_dir,
                        verbose=False,
                    )

                    # Temporary directory should be cleaned up
                    assert not temp_dir.exists()

    def test_temporary_directory_cleanup_on_error(self, sample_package, tmp_path, mock_config):
        """Test that temporary directory is cleaned up even on error."""
        output_dir = tmp_path / "output"

        temp_dir = tmp_path / "temp_sbom_cleanup_error"
        temp_dir.mkdir()

        with config_context(mock_config):
            with patch("cve_report_aggregator.core.executor.ExecutorManager.create_temp_directory") as mock_mktemp:
                with patch("cve_report_aggregator.core.executor.ExecutorManager.execute") as mock_execute:
                    # mktemp succeeds, uds fails
                    mock_mktemp.return_value = (temp_dir, None)
                    mock_execute.return_value = ("", RuntimeError("uds failed"))

                    with pytest.raises(RuntimeError):
                        download_package_sbom(
                            package=sample_package,
                            registry="registry.example.com",
                            organization="test-org",
                            output_dir=output_dir,
                        )

                    # Temporary directory should still be cleaned up
                    assert not temp_dir.exists()

    def test_verbose_logging(self, sample_package, tmp_path, mock_config):
        """Test verbose logging output."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        temp_dir = tmp_path / "temp_sbom_verbose"
        temp_dir.mkdir()

        package_temp_dir = temp_dir / f"{sample_package.name}-sbom"
        package_temp_dir.mkdir()
        (package_temp_dir / "sbom.json").write_text('{"test": "data"}')

        with config_context(mock_config):
            with patch("cve_report_aggregator.core.executor.ExecutorManager.create_temp_directory") as mock_mktemp:
                with patch("cve_report_aggregator.core.executor.ExecutorManager.execute") as mock_execute:
                    mock_mktemp.return_value = (temp_dir, None)
                    mock_execute.return_value = ("", None)

                    with patch("cve_report_aggregator.io.downloader.logger") as mock_logger:
                        download_package_sbom(
                            package=sample_package,
                            registry="registry.example.com",
                            organization="test-org",
                            output_dir=output_dir,
                            verbose=True,
                        )

                        # Verify logging calls
                        assert mock_logger.info.called
                        assert mock_logger.debug.called

    def test_sbom_file_naming(self, sample_package, tmp_path, mock_config):
        """Test that SBOM files are named correctly in output directory."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        temp_dir = tmp_path / "temp_sbom_naming"
        temp_dir.mkdir()

        package_temp_dir = temp_dir / f"{sample_package.name}-sbom"
        package_temp_dir.mkdir()

        # Create SBOM with specific name
        (package_temp_dir / "component-sbom.json").write_text('{"test": "data"}')

        with config_context(mock_config):
            with patch("cve_report_aggregator.core.executor.ExecutorManager.create_temp_directory") as mock_mktemp:
                with patch("cve_report_aggregator.core.executor.ExecutorManager.execute") as mock_execute:
                    mock_mktemp.return_value = (temp_dir, None)
                    mock_execute.return_value = ("", None)

                    result = download_package_sbom(
                        package=sample_package,
                        registry="registry.example.com",
                        organization="test-org",
                        output_dir=output_dir,
                        verbose=False,
                    )

                    assert len(result) == 1
                    # Should be named: <package-name>-<version>-<original-filename>
                    expected_name = f"{sample_package.name}-{sample_package.version}-component-sbom.json"
                    assert result[0].name == expected_name

    def test_multiple_json_files_in_directory(self, sample_package, tmp_path, mock_config):
        """Test handling multiple JSON files in downloaded directory."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        temp_dir = tmp_path / "temp_sbom_multiple"
        temp_dir.mkdir()

        package_temp_dir = temp_dir / f"{sample_package.name}-sbom"
        package_temp_dir.mkdir()

        # Create multiple JSON files at different levels
        (package_temp_dir / "sbom1.json").write_text('{"test": "data1"}')
        (package_temp_dir / "sbom2.json").write_text('{"test": "data2"}')

        subdir = package_temp_dir / "layers"
        subdir.mkdir()
        (subdir / "layer-sbom.json").write_text('{"test": "data3"}')

        with config_context(mock_config):
            with patch("cve_report_aggregator.core.executor.ExecutorManager.create_temp_directory") as mock_mktemp:
                with patch("cve_report_aggregator.core.executor.ExecutorManager.execute") as mock_execute:
                    mock_mktemp.return_value = (temp_dir, None)
                    mock_execute.return_value = ("", None)

                    result = download_package_sbom(
                        package=sample_package,
                        registry="registry.example.com",
                        organization="test-org",
                        output_dir=output_dir,
                        verbose=False,
                    )

                    # Should find all JSON files recursively
                    assert len(result) == 3
                    assert all(f.exists() for f in result)

    def test_package_reference_construction(self, sample_package, tmp_path, mock_config):
        """Test correct construction of package reference."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        temp_dir = tmp_path / "temp_sbom_ref"
        temp_dir.mkdir()

        package_temp_dir = temp_dir / f"{sample_package.name}-sbom"
        package_temp_dir.mkdir()

        with config_context(mock_config):
            with patch("cve_report_aggregator.core.executor.ExecutorManager.create_temp_directory") as mock_mktemp:
                with patch("cve_report_aggregator.core.executor.ExecutorManager.execute") as mock_execute:
                    mock_mktemp.return_value = (temp_dir, None)
                    mock_execute.return_value = ("", None)

                    download_package_sbom(
                        package=sample_package,
                        registry="custom.registry.io",
                        organization="my-org",
                        output_dir=output_dir,
                        verbose=False,
                    )

                    # Check the uds command call
                    uds_call = mock_execute.call_args[0][0]
                    package_ref = uds_call[5]

                    # Format should be: <registry>/<organization>/<package-name>-<version>
                    expected_ref = f"custom.registry.io/my-org/{sample_package.name}-{sample_package.version}"
                    assert package_ref == expected_ref

    def test_architecture_parameter(self, sample_package, tmp_path, mock_config):
        """Test that architecture parameter is correctly passed to uds command."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        temp_dir = tmp_path / "temp_sbom_arch"
        temp_dir.mkdir()

        package_temp_dir = temp_dir / f"{sample_package.name}-sbom"
        package_temp_dir.mkdir()

        # Test with arm64 architecture
        arm_package = PackageConfig(name=sample_package.name, version=sample_package.version, architecture="arm64")

        with config_context(mock_config):
            with patch("cve_report_aggregator.core.executor.ExecutorManager.create_temp_directory") as mock_mktemp:
                with patch("cve_report_aggregator.core.executor.ExecutorManager.execute") as mock_execute:
                    mock_mktemp.return_value = (temp_dir, None)
                    mock_execute.return_value = ("", None)

                    download_package_sbom(
                        package=arm_package,
                        registry="registry.example.com",
                        organization="test-org",
                        output_dir=output_dir,
                        verbose=False,
                    )

                    # Check the uds command call
                    uds_call = mock_execute.call_args[0][0]

                    # Find architecture flag
                    arch_index = uds_call.index("-a")
                    assert uds_call[arch_index + 1] == "arm64"

    @pytest.mark.parametrize(
        "package_config,expected_error",
        [
            (
                PackageConfig(name="", version="1.0.0", architecture="amd64"),
                "Package name is required",
            ),
            (PackageConfig(name="test", version="", architecture="amd64"), "Package version is required"),
            (PackageConfig(name="test", version="1.0.0", architecture=""), "Package architecture is required"),
        ],
    )
    def test_package_validation_errors(self, package_config, expected_error, tmp_path, mock_config):
        """Test package validation with various invalid configurations."""
        output_dir = tmp_path / "output"

        with config_context(mock_config):
            with pytest.raises(ValueError, match=expected_error):
                download_package_sbom(
                    package=package_config,
                    registry="registry.example.com",
                    organization="test-org",
                    output_dir=output_dir,
                )

    def test_get_current_config_integration(self, sample_package, tmp_path, mock_config):
        """Test integration with get_current_config for command execution."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        temp_dir = tmp_path / "temp_sbom_config"
        temp_dir.mkdir()

        package_temp_dir = temp_dir / f"{sample_package.name}-sbom"
        package_temp_dir.mkdir()

        with config_context(mock_config):
            with patch("cve_report_aggregator.core.executor.ExecutorManager.create_temp_directory") as mock_mktemp:
                with patch("cve_report_aggregator.core.executor.ExecutorManager.execute") as mock_execute:
                    mock_mktemp.return_value = (temp_dir, None)
                    mock_execute.return_value = ("", None)

                    download_package_sbom(
                        package=sample_package,
                        registry="registry.example.com",
                        organization="test-org",
                        output_dir=output_dir,
                        verbose=False,
                    )

                    # Verify ExecutorManager.execute was called
                    mock_execute.assert_called_once()
                    # Verify config parameter was passed
                    call_kwargs = mock_execute.call_args.kwargs
                    assert "config" in call_kwargs
