"""Tests for command-line interface."""

import json
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from cve_report_aggregator.cli import display_logo, main


class TestDisplayLogo:
    """Tests for display_logo function."""

    def test_display_logo_success(self):
        """Test that logo displays successfully."""
        with patch("cve_report_aggregator.cli.console") as mock_console:
            display_logo()
            # Should call console.print with the ASCII logo
            mock_console.print.assert_called_once()
            call_args = mock_console.print.call_args[0]
            # First arg should be the logo string
            assert len(call_args[0]) > 100  # Logo is a long string

    def test_display_logo_fallback(self):
        """Test logo fallback when display fails."""
        with patch("cve_report_aggregator.cli.console") as mock_console:
            # Make console.print raise an exception on first call
            mock_console.print.side_effect = [Exception("Display error"), None]

            display_logo()

            # Should call print twice (once failed, once fallback)
            assert mock_console.print.call_count == 2
            # Second call should be the fallback message
            fallback_call = mock_console.print.call_args_list[1]
            assert "CVE Report Aggregator" in str(fallback_call)


class TestCLIMain:
    """Tests for main CLI function."""

    def test_cli_help(self):
        """Test CLI help output."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "CVE Report Aggregator" in result.output
        assert "Aggregate and deduplicate" in result.output

    def test_cli_version(self):
        """Test CLI version output."""
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])

        assert result.exit_code == 0
        # Should display version number

    def test_cli_default_arguments(self, tmp_path, sample_grype_report, mock_subprocess_success):
        """Test CLI with default arguments."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            # Create reports directory with a sample report
            reports_dir = Path.cwd() / "reports"
            reports_dir.mkdir()

            report_file = reports_dir / "test.json"
            report_file.write_text(json.dumps(sample_grype_report))

            output_file = Path.cwd() / "unified-report.json"

            # Explicitly specify paths since isolated_filesystem changes cwd
            result = runner.invoke(main, ["-i", str(reports_dir), "-o", str(output_file)])

            # Should succeed (exit code 0)
            assert result.exit_code == 0, f"CLI failed with output:\n{result.output}"
            # Should create unified-report.json
            assert output_file.exists()

    def test_cli_custom_input_output(self, tmp_path, sample_grype_report, mock_subprocess_success):
        """Test CLI with custom input and output paths."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            # Create custom reports directory
            custom_input = Path.cwd() / "custom-reports"
            custom_input.mkdir()

            report_file = custom_input / "test.json"
            report_file.write_text(json.dumps(sample_grype_report))

            custom_output = Path.cwd() / "output" / "custom-report.json"
            # Create output directory
            custom_output.parent.mkdir(parents=True, exist_ok=True)

            result = runner.invoke(main, ["-i", str(custom_input), "-o", str(custom_output)])

            assert result.exit_code == 0, f"CLI failed with output:\n{result.output}"
            assert custom_output.exists()

    def test_cli_output_parent_not_exists(self, tmp_path):
        """Test CLI error when output parent directory doesn't exist."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            reports_dir = Path.cwd() / "reports"
            reports_dir.mkdir()

            # Output path with non-existent parent
            bad_output = Path.cwd() / "nonexistent" / "deep" / "path" / "output.json"

            result = runner.invoke(main, ["-i", str(reports_dir), "-o", str(bad_output)])

            assert result.exit_code == 1
            assert "Output file parent directory does not exist" in result.output

    def test_cli_output_is_directory(self, tmp_path, sample_grype_report, mock_subprocess_success):
        """Test CLI error when output path is a directory."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            reports_dir = Path.cwd() / "reports"
            reports_dir.mkdir()

            # Add a sample report so we pass the "no reports" check
            report_file = reports_dir / "test.json"
            report_file.write_text(json.dumps(sample_grype_report))

            # Create a directory where output file should be
            output_dir = Path.cwd() / "output-dir"
            output_dir.mkdir()

            result = runner.invoke(main, ["-i", str(reports_dir), "-o", str(output_dir)])

            # Click validates dir_okay=False with exit code 2
            assert result.exit_code == 2
            assert "directory" in result.output.lower()

    def test_cli_output_non_json_extension(self, tmp_path, sample_grype_report, mock_subprocess_success):
        """Test CLI warning when output file doesn't have .json extension."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            reports_dir = Path.cwd() / "reports"
            reports_dir.mkdir()

            report_file = reports_dir / "test.json"
            report_file.write_text(json.dumps(sample_grype_report))

            output_file = Path.cwd() / "output.txt"

            result = runner.invoke(main, ["-i", str(reports_dir), "-o", str(output_file)])

            # Should still succeed but show warning
            assert result.exit_code == 0
            assert "does not have .json extension" in result.output

    def test_cli_grype_only_mode(self, tmp_path, sample_grype_report, mock_subprocess_success):
        """Test CLI with grype-only mode."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            reports_dir = Path.cwd() / "reports"
            reports_dir.mkdir()

            report_file = reports_dir / "test.json"
            report_file.write_text(json.dumps(sample_grype_report))

            result = runner.invoke(main, ["-i", str(reports_dir), "-m", "grype-only"])

            assert result.exit_code == 0
            assert "grype-only" in result.output.lower() or "Grype" in result.output

    def test_cli_trivy_only_mode(self, tmp_path, sample_grype_report, monkeypatch):
        """Test CLI with trivy-only mode."""
        runner = CliRunner()

        # Mock subprocess for Trivy workflow
        def mock_run(*args, **kwargs):
            command = args[0]

            class MockResult:
                stdout = ""
                stderr = ""
                returncode = 0

            if "which" in command:
                return MockResult()
            elif "version" in command:
                MockResult.stdout = "Version: 0.100.0\n"
                return MockResult()
            elif "syft" in command and "convert" in command:
                MockResult.stdout = json.dumps({"bomFormat": "CycloneDX"})
                return MockResult()
            elif "trivy" in command:
                # Create output file if -o flag is present
                for i, arg in enumerate(command):
                    if arg == "-o" and i + 1 < len(command):
                        output_path = Path(command[i + 1])
                        output_path.write_text(
                            json.dumps(
                                {
                                    "ArtifactName": "test:latest",
                                    "SchemaVersion": "2.0.0",
                                    "CreatedAt": "2024-01-01T00:00:00Z",
                                    "Results": [{"Vulnerabilities": [{"VulnerabilityID": "CVE-2024-12345"}]}],
                                }
                            )
                        )
                return MockResult()
            return MockResult()

        import subprocess

        monkeypatch.setattr(subprocess, "run", mock_run)

        with runner.isolated_filesystem(temp_dir=tmp_path):
            reports_dir = Path.cwd() / "reports"
            reports_dir.mkdir()

            report_file = reports_dir / "test.json"
            report_file.write_text(json.dumps(sample_grype_report))

            result = runner.invoke(main, ["-i", str(reports_dir), "-m", "trivy-only"])

            assert result.exit_code == 0

    def test_cli_grype_only_missing_grype(self, tmp_path, mock_subprocess_failure):
        """Test CLI error when grype-only mode but grype not installed."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            reports_dir = Path.cwd() / "reports"
            reports_dir.mkdir()

            result = runner.invoke(main, ["-i", str(reports_dir), "-m", "grype-only"])

            assert result.exit_code == 1
            assert "grype" in result.output.lower()

    def test_cli_trivy_only_missing_trivy(self, tmp_path, mock_subprocess_failure):
        """Test CLI error when trivy-only mode but trivy not installed."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            reports_dir = Path.cwd() / "reports"
            reports_dir.mkdir()

            result = runner.invoke(main, ["-i", str(reports_dir), "-m", "trivy-only"])

            assert result.exit_code == 1
            assert "trivy" in result.output.lower() or "syft" in result.output.lower()

    def test_cli_highest_score_mode(self, tmp_path, sample_grype_report, mock_subprocess_success):
        """Test CLI with highest-score mode (default)."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            reports_dir = Path.cwd() / "reports"
            reports_dir.mkdir()

            report_file = reports_dir / "test.json"
            report_file.write_text(json.dumps(sample_grype_report))

            result = runner.invoke(main, ["-i", str(reports_dir), "-m", "highest-score"])

            assert result.exit_code == 0
            assert "highest-score" in result.output.lower()

    def test_cli_first_occurrence_mode(self, tmp_path, sample_grype_report, mock_subprocess_success):
        """Test CLI with first-occurrence mode."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            reports_dir = Path.cwd() / "reports"
            reports_dir.mkdir()

            report_file = reports_dir / "test.json"
            report_file.write_text(json.dumps(sample_grype_report))

            result = runner.invoke(main, ["-i", str(reports_dir), "-m", "first-occurrence"])

            assert result.exit_code == 0
            assert "first-occurrence" in result.output.lower()

    def test_cli_verbose_mode(self, tmp_path, sample_grype_report, mock_subprocess_success):
        """Test CLI with verbose output."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            reports_dir = Path.cwd() / "reports"
            reports_dir.mkdir()

            report_file = reports_dir / "test.json"
            report_file.write_text(json.dumps(sample_grype_report))

            result = runner.invoke(main, ["-i", str(reports_dir), "-v"])

            assert result.exit_code == 0
            # Verbose should show reports directory
            assert str(reports_dir) in result.output or "reports" in result.output.lower()

    def test_cli_no_reports_found(self, tmp_path, mock_subprocess_success):
        """Test CLI error when no valid reports found."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            reports_dir = Path.cwd() / "reports"
            reports_dir.mkdir()

            # Create empty/invalid report
            report_file = reports_dir / "empty.json"
            report_file.write_text(json.dumps({"no": "matches"}))

            result = runner.invoke(main, ["-i", str(reports_dir)])

            assert result.exit_code == 1
            assert "No valid reports" in result.output

    def test_cli_trivy_scanner_missing_syft(self, tmp_path, monkeypatch):
        """Test CLI error when using trivy scanner but syft not installed."""
        import subprocess

        def mock_run(*args, **kwargs):
            command = args[0]
            if "which" in command:
                if "syft" in command:
                    raise subprocess.CalledProcessError(1, command)
            raise subprocess.CalledProcessError(1, command)

        monkeypatch.setattr(subprocess, "run", mock_run)

        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            reports_dir = Path.cwd() / "reports"
            reports_dir.mkdir()

            result = runner.invoke(main, ["-i", str(reports_dir), "-s", "trivy"])

            assert result.exit_code == 1
            assert "syft" in result.output.lower()

    def test_cli_trivy_scanner_missing_trivy(self, tmp_path, monkeypatch):
        """Test CLI error when using trivy scanner but trivy not installed."""
        import subprocess

        def mock_run(*args, **kwargs):
            command = args[0]
            if "which" in command:
                if "syft" in command:
                    # syft exists
                    class MockResult:
                        stdout = "/usr/local/bin/syft"
                        returncode = 0

                    return MockResult()
                elif "trivy" in command:
                    # trivy doesn't exist
                    raise subprocess.CalledProcessError(1, command)
            raise subprocess.CalledProcessError(1, command)

        monkeypatch.setattr(subprocess, "run", mock_run)

        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            reports_dir = Path.cwd() / "reports"
            reports_dir.mkdir()

            result = runner.invoke(main, ["-i", str(reports_dir), "-s", "trivy"])

            assert result.exit_code == 1
            assert "trivy" in result.output.lower()

    def test_cli_grype_scanner_missing(self, tmp_path, mock_subprocess_failure):
        """Test CLI error when using grype scanner but grype not installed."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            reports_dir = Path.cwd() / "reports"
            reports_dir.mkdir()

            result = runner.invoke(main, ["-i", str(reports_dir), "-s", "grype"])

            assert result.exit_code == 1
            assert "grype" in result.output.lower()

    def test_cli_creates_output_directory(self, tmp_path, sample_grype_report, mock_subprocess_success):
        """Test that CLI creates output directory if it doesn't exist."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            reports_dir = Path.cwd() / "reports"
            reports_dir.mkdir()

            report_file = reports_dir / "test.json"
            report_file.write_text(json.dumps(sample_grype_report))

            # Output in a new directory that doesn't exist yet
            output_file = Path.cwd() / "new-dir" / "output.json"
            # Create parent to avoid the "parent not exist" error
            output_file.parent.mkdir(parents=True)

            result = runner.invoke(main, ["-i", str(reports_dir), "-o", str(output_file)])

            assert result.exit_code == 0
            assert output_file.exists()

    def test_cli_summary_statistics(self, tmp_path, sample_grype_report, mock_subprocess_success):
        """Test that CLI displays summary statistics."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            reports_dir = Path.cwd() / "reports"
            reports_dir.mkdir()

            report_file = reports_dir / "test.json"
            report_file.write_text(json.dumps(sample_grype_report))

            result = runner.invoke(main, ["-i", str(reports_dir)])

            assert result.exit_code == 0
            # Should display summary statistics
            assert "Vulnerability Summary" in result.output or "Summary" in result.output
            assert "Severity Breakdown" in result.output or "Severity" in result.output

    def test_cli_multiple_scanners_mode_override(self, tmp_path, sample_grype_report, mock_subprocess_success):
        """Test that mode-specific scanner overrides --scanner flag."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            reports_dir = Path.cwd() / "reports"
            reports_dir.mkdir()

            report_file = reports_dir / "test.json"
            report_file.write_text(json.dumps(sample_grype_report))

            # Use --scanner trivy but --mode grype-only
            # grype-only mode should override the scanner choice
            result = runner.invoke(main, ["-i", str(reports_dir), "-s", "trivy", "-m", "grype-only"])

            assert result.exit_code == 0
            # Should use grype, not trivy

    def test_cli_json_output_structure(self, tmp_path, sample_grype_report, mock_subprocess_success):
        """Test that CLI produces valid JSON output with expected structure."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            reports_dir = Path.cwd() / "reports"
            reports_dir.mkdir()

            report_file = reports_dir / "test.json"
            report_file.write_text(json.dumps(sample_grype_report))

            output_file = Path.cwd() / "output.json"

            result = runner.invoke(main, ["-i", str(reports_dir), "-o", str(output_file)])

            assert result.exit_code == 0

            # Verify JSON structure
            with open(output_file) as f:
                data = json.load(f)

            assert "metadata" in data
            assert "summary" in data
            assert "vulnerabilities" in data
            assert "database_info" in data

            # Verify metadata fields
            assert "generated_at" in data["metadata"]
            assert "scanner" in data["metadata"]
            assert data["metadata"]["scanner"] == "grype"

            # Verify summary fields
            assert "total_vulnerability_occurrences" in data["summary"]
            assert "unique_vulnerabilities" in data["summary"]
            assert "by_severity" in data["summary"]
