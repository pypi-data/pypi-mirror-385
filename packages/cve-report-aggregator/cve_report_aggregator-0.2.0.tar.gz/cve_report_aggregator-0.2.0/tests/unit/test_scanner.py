"""Tests for scanner integration functionality."""

import json
import subprocess
from pathlib import Path

import pytest

from cve_report_aggregator.scanner import convert_to_cyclonedx, load_reports, process_trivy_reports, scan_with_trivy


class TestConvertToCycloneDX:
    """Tests for convert_to_cyclonedx function."""

    def test_convert_grype_to_cyclonedx(self, tmp_path, mock_subprocess_success):
        """Test converting Grype report to CycloneDX format."""
        # Create a fake Grype report
        grype_report = tmp_path / "grype-report.json"
        grype_report.write_text(json.dumps({"matches": []}))

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        cdx_file = convert_to_cyclonedx(grype_report, output_dir, verbose=False)

        assert cdx_file.exists()
        assert cdx_file.name == "grype-report.cdx.json"
        data = json.loads(cdx_file.read_text())
        assert "bomFormat" in data
        assert data["bomFormat"] == "CycloneDX"

    def test_convert_with_verbose_output(self, tmp_path, mock_subprocess_success, capsys):
        """Test conversion with verbose output enabled."""
        grype_report = tmp_path / "test.json"
        grype_report.write_text(json.dumps({}))

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        convert_to_cyclonedx(grype_report, output_dir, verbose=True)

        # Verbose mode should print messages (captured by Rich console)
        # We can't easily test Rich output, but we can verify no errors

    def test_convert_syft_error(self, tmp_path, mock_subprocess_failure):
        """Test handling syft conversion errors."""
        grype_report = tmp_path / "test.json"
        grype_report.write_text(json.dumps({}))

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with pytest.raises(subprocess.CalledProcessError):
            convert_to_cyclonedx(grype_report, output_dir, verbose=False)

    def test_convert_syft_not_found(self, tmp_path, mock_subprocess_not_found):
        """Test handling when syft command not found."""
        grype_report = tmp_path / "test.json"
        grype_report.write_text(json.dumps({}))

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with pytest.raises(SystemExit):
            convert_to_cyclonedx(grype_report, output_dir, verbose=False)


class TestScanWithTrivy:
    """Tests for scan_with_trivy function."""

    def test_scan_cyclonedx_with_trivy(self, tmp_path, monkeypatch):
        """Test scanning CycloneDX SBOM with Trivy."""
        cdx_file = tmp_path / "test.cdx.json"
        cdx_file.write_text(json.dumps({"bomFormat": "CycloneDX"}))

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Mock subprocess to create the output file
        import subprocess

        def mock_run(*args, **kwargs):
            command = args[0]
            if "trivy" in command:
                # Find the output file path from the command
                for i, arg in enumerate(command):
                    if arg == "-o" and i + 1 < len(command):
                        output_path = Path(command[i + 1])
                        # Create the output file with sample Trivy data
                        output_path.write_text(
                            json.dumps(
                                {
                                    "ArtifactName": "test:latest",
                                    "SchemaVersion": "2.0.0",
                                    "CreatedAt": "2024-01-01T00:00:00Z",
                                    "Results": [],
                                }
                            )
                        )
                        break

            class MockResult:
                stdout = ""
                stderr = ""
                returncode = 0

            return MockResult()

        monkeypatch.setattr(subprocess, "run", mock_run)

        trivy_report = scan_with_trivy(cdx_file, output_dir, verbose=False)

        assert trivy_report.exists()
        assert trivy_report.name == "test.trivy.json"

    def test_scan_with_verbose(self, tmp_path, mock_subprocess_success):
        """Test Trivy scanning with verbose output."""
        cdx_file = tmp_path / "test.cdx.json"
        cdx_file.write_text(json.dumps({}))

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        scan_with_trivy(cdx_file, output_dir, verbose=True)
        # Should not raise errors

    def test_scan_trivy_error(self, tmp_path, mock_subprocess_failure):
        """Test handling Trivy scan errors."""
        cdx_file = tmp_path / "test.cdx.json"
        cdx_file.write_text(json.dumps({}))

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with pytest.raises(subprocess.CalledProcessError):
            scan_with_trivy(cdx_file, output_dir, verbose=False)

    def test_scan_trivy_not_found(self, tmp_path, mock_subprocess_not_found):
        """Test handling when trivy command not found."""
        cdx_file = tmp_path / "test.cdx.json"
        cdx_file.write_text(json.dumps({}))

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with pytest.raises(SystemExit):
            scan_with_trivy(cdx_file, output_dir, verbose=False)


class TestProcessTrivyReports:
    """Tests for process_trivy_reports function."""

    def test_process_empty_directory(self, tmp_path):
        """Test processing directory with no JSON files."""
        with pytest.raises(SystemExit):
            process_trivy_reports(tmp_path, verbose=False)

    def test_process_grype_reports(self, tmp_path, sample_grype_report, monkeypatch):
        """Test processing Grype reports and converting to Trivy."""
        # Create a Grype report file
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()

        report_file = reports_dir / "test.json"
        report_file.write_text(json.dumps(sample_grype_report))

        # Mock subprocess to avoid actual tool execution
        def mock_run(*args, **kwargs):
            command = args[0]

            class MockResult:
                stdout = ""
                stderr = ""
                returncode = 0

            if "syft" in command and "convert" in command:
                MockResult.stdout = json.dumps({"bomFormat": "CycloneDX"})
            elif "trivy" in command:
                # Create the output file
                output_file = None
                for i, arg in enumerate(command):
                    if arg == "-o" and i + 1 < len(command):
                        output_file = Path(command[i + 1])
                        break

                if output_file:
                    trivy_data = {
                        "ArtifactName": "test:latest",
                        "Results": [{"Vulnerabilities": [{"VulnerabilityID": "CVE-2024-12345"}]}],
                    }
                    output_file.write_text(json.dumps(trivy_data))

            return MockResult()

        monkeypatch.setattr(subprocess, "run", mock_run)

        reports = process_trivy_reports(reports_dir, verbose=False)

        assert len(reports) == 1
        assert reports[0]["_scanner"] == "trivy"
        assert reports[0]["_source_file"] == "test.json"

    def test_process_with_conversion_error(self, tmp_path, sample_grype_report, monkeypatch):
        """Test handling conversion errors gracefully."""
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()

        report_file = reports_dir / "test.json"
        report_file.write_text(json.dumps(sample_grype_report))

        def mock_run(*args, **kwargs):
            raise subprocess.CalledProcessError(1, args[0], stderr="Error")

        monkeypatch.setattr(subprocess, "run", mock_run)

        # Should not crash, but return empty list
        reports = process_trivy_reports(reports_dir, verbose=False)
        assert len(reports) == 0


class TestLoadReports:
    """Tests for load_reports function."""

    def test_load_grype_reports(self, temp_reports_dir):
        """Test loading Grype reports from directory."""
        reports = load_reports(temp_reports_dir, scanner="grype", verbose=False)

        assert len(reports) == 1
        assert reports[0]["_scanner"] == "grype"
        assert reports[0]["_source_file"] == "test-report.json"
        assert len(reports[0]["matches"]) == 1

    def test_load_grype_reports_verbose(self, temp_reports_dir, capsys):
        """Test loading reports with verbose output."""
        reports = load_reports(temp_reports_dir, scanner="grype", verbose=True)
        assert len(reports) == 1

    def test_load_reports_no_json_files(self, tmp_path):
        """Test loading from directory with no JSON files."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        with pytest.raises(SystemExit):
            load_reports(empty_dir, scanner="grype", verbose=False)

    def test_load_reports_invalid_json(self, tmp_path):
        """Test handling invalid JSON files."""
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()

        # Create invalid JSON file
        invalid_file = reports_dir / "invalid.json"
        invalid_file.write_text("{ this is not valid json")

        reports = load_reports(reports_dir, scanner="grype", verbose=False)
        assert len(reports) == 0  # Should skip invalid files

    def test_load_reports_no_matches(self, tmp_path):
        """Test handling reports without matches."""
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()

        # Report without matches field
        report_file = reports_dir / "no-matches.json"
        report_file.write_text(json.dumps({"source": {}, "descriptor": {}}))

        reports = load_reports(reports_dir, scanner="grype", verbose=False)
        assert len(reports) == 0

    def test_load_sbom_and_scan(self, tmp_path, sample_sbom_report, mock_subprocess_success):
        """Test detecting and scanning SBOM files."""
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()

        sbom_file = reports_dir / "sbom.json"
        sbom_file.write_text(json.dumps(sample_sbom_report))

        reports = load_reports(reports_dir, scanner="grype", verbose=False)

        # Should have scanned the SBOM
        assert len(reports) == 1
        assert reports[0]["_scanner"] == "grype"

    def test_load_sbom_scan_error(self, tmp_path, sample_sbom_report, mock_subprocess_failure):
        """Test handling SBOM scan errors."""
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()

        sbom_file = reports_dir / "sbom.json"
        sbom_file.write_text(json.dumps(sample_sbom_report))

        reports = load_reports(reports_dir, scanner="grype", verbose=False)
        # Should skip failed scans
        assert len(reports) == 0

    def test_load_sbom_no_vulnerabilities(self, tmp_path, sample_sbom_report, monkeypatch):
        """Test SBOM scan that finds no vulnerabilities."""
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()

        sbom_file = reports_dir / "sbom.json"
        sbom_file.write_text(json.dumps(sample_sbom_report))

        class MockResult:
            stdout = json.dumps({"matches": []})  # No matches
            stderr = ""
            returncode = 0

        def mock_run(*args, **kwargs):
            return MockResult()

        monkeypatch.setattr(subprocess, "run", mock_run)

        reports = load_reports(reports_dir, scanner="grype", verbose=True)
        assert len(reports) == 0

    def test_load_sbom_invalid_grype_output(self, tmp_path, sample_sbom_report, monkeypatch):
        """Test handling invalid Grype scan output."""
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()

        sbom_file = reports_dir / "sbom.json"
        sbom_file.write_text(json.dumps(sample_sbom_report))

        class MockResult:
            stdout = "not valid json"
            stderr = ""
            returncode = 0

        def mock_run(*args, **kwargs):
            return MockResult()

        monkeypatch.setattr(subprocess, "run", mock_run)

        reports = load_reports(reports_dir, scanner="grype", verbose=False)
        assert len(reports) == 0

    def test_load_unknown_format(self, tmp_path):
        """Test handling unknown file formats."""
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()

        # Unknown format (not Grype report, not SBOM)
        unknown_file = reports_dir / "unknown.json"
        unknown_file.write_text(json.dumps({"some": "data", "but": "not recognized"}))

        reports = load_reports(reports_dir, scanner="grype", verbose=True)
        assert len(reports) == 0

    def test_load_trivy_scanner(self, tmp_path, sample_grype_report, monkeypatch):
        """Test loading reports with Trivy scanner."""
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()

        report_file = reports_dir / "test.json"
        report_file.write_text(json.dumps(sample_grype_report))

        def mock_run(*args, **kwargs):
            command = args[0]

            class MockResult:
                stdout = ""
                stderr = ""
                returncode = 0

            if "syft" in command and "convert" in command:
                MockResult.stdout = json.dumps({"bomFormat": "CycloneDX"})
            elif "trivy" in command:
                output_file = None
                for i, arg in enumerate(command):
                    if arg == "-o" and i + 1 < len(command):
                        output_file = Path(command[i + 1])
                        break

                if output_file:
                    output_file.write_text(
                        json.dumps(
                            {
                                "ArtifactName": "test:latest",
                                "Results": [{"Vulnerabilities": [{"VulnerabilityID": "CVE-2024-12345"}]}],
                            }
                        )
                    )

            return MockResult()

        monkeypatch.setattr(subprocess, "run", mock_run)

        reports = load_reports(reports_dir, scanner="trivy", verbose=False)
        assert len(reports) == 1
        assert reports[0]["_scanner"] == "trivy"

    def test_load_reports_general_exception(self, tmp_path, monkeypatch):
        """Test handling general exceptions during file loading."""
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()

        report_file = reports_dir / "test.json"
        report_file.write_text(json.dumps({"matches": []}))

        # Monkeypatch json.load to raise an exception
        original_open = open

        def mock_open(*args, **kwargs):
            f = original_open(*args, **kwargs)
            if "test.json" in str(args[0]):
                # Make json.load raise an exception
                import json as json_module

                # original_load = json_module.load

                def raise_error(*args, **kwargs):
                    raise ValueError("Unexpected error")

                monkeypatch.setattr(json_module, "load", raise_error)
            return f

        monkeypatch.setattr("builtins.open", mock_open)

        reports = load_reports(reports_dir, scanner="grype", verbose=False)
        # Should handle exception and skip file
        assert len(reports) == 0

    def test_load_multiple_reports(self, tmp_path, sample_grype_report):
        """Test loading multiple valid reports."""
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()

        # Create multiple reports
        for i in range(3):
            report = sample_grype_report.copy()
            report["_source_file"] = f"report{i}.json"
            report_file = reports_dir / f"report{i}.json"
            report_file.write_text(json.dumps(report))

        reports = load_reports(reports_dir, scanner="grype", verbose=False)
        assert len(reports) == 3
