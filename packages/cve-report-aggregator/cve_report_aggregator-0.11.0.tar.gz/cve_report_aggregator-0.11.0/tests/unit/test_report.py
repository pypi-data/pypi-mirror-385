"""Tests for report generation functionality."""

import copy

from cve_report_aggregator.io.report import create_unified_report


class TestCreateUnifiedReport:
    """Tests for create_unified_report function."""

    def test_create_report_with_grype_data(self, vuln_map_sample, sample_grype_report):
        """Test creating unified report from Grype data."""
        reports = [sample_grype_report]
        report = create_unified_report(vuln_map_sample, reports)

        # Verify metadata
        assert "metadata" in report
        assert report["metadata"]["scanner"] == "grype"
        assert report["metadata"]["scanner_version"] == "0.100.0"
        assert report["metadata"]["source_reports_count"] == 1
        assert "test-report.json" in report["metadata"]["source_reports"]

        # Verify summary
        assert "summary" in report
        assert report["summary"]["total_vulnerability_occurrences"] == 3  # 2 + 1
        assert report["summary"]["unique_vulnerabilities"] == 2

        # Verify severity breakdown
        assert "by_severity" in report["summary"]
        severity = report["summary"]["by_severity"]
        assert severity["High"] == 2
        assert severity["Critical"] == 1
        assert severity["Medium"] == 0
        assert severity["Low"] == 0

        # Verify vulnerabilities
        assert "vulnerabilities" in report
        assert len(report["vulnerabilities"]) == 2

        # Verify sorting (by count, descending)
        assert report["vulnerabilities"][0]["count"] >= report["vulnerabilities"][1]["count"]

        # Verify database info
        assert "database_info" in report
        assert report["database_info"]["built"] == "2024-01-01T00:00:00Z"
        assert report["database_info"]["schemaVersion"] == 5

    def test_create_report_with_trivy_data(self, vuln_map_sample, sample_trivy_report):
        """Test creating unified report from Trivy data."""
        reports = [sample_trivy_report]
        report = create_unified_report(vuln_map_sample, reports)

        # Verify metadata
        assert report["metadata"]["scanner"] == "trivy"
        assert report["metadata"]["scanner_version"] == "2.0.0"

        # Verify scanned images for Trivy format
        assert len(report["summary"]["scanned_images"]) == 1
        scanned = report["summary"]["scanned_images"][0]
        assert scanned["file"] == "test-trivy-report.json"
        assert scanned["image"] == "nginx:1.21"
        assert scanned["matches"] == 1

        # Verify database info for Trivy
        assert report["database_info"]["schema_version"] == "2.0.0"
        assert report["database_info"]["created_at"] == "2024-01-01T00:00:00Z"

    def test_create_report_empty_reports(self, vuln_map_sample):
        """Test creating report with empty reports list."""
        report = create_unified_report(vuln_map_sample, [])

        assert report["metadata"]["source_reports_count"] == 0
        assert report["metadata"]["scanner"] == "grype"  # Default
        assert report["summary"]["scanned_images"] == []

    def test_create_report_severity_normalization(self, sample_grype_report):
        """Test that severity values are normalized (title case)."""
        vuln_map = {
            "CVE-2024-11111": {
                "count": 1,
                "selected_scanner": "grype",
                "vulnerability_data": {
                    "id": "CVE-2024-11111",
                    "severity": "high",  # Lowercase
                },
                "related_vulnerabilities": [],
                "affected_sources": [],
                "match_details": [],
            },
            "CVE-2024-22222": {
                "count": 1,
                "selected_scanner": "grype",
                "vulnerability_data": {
                    "id": "CVE-2024-22222",
                    "severity": "CRITICAL",  # Uppercase
                },
                "related_vulnerabilities": [],
                "affected_sources": [],
                "match_details": [],
            },
        }

        reports = [sample_grype_report]
        report = create_unified_report(vuln_map, reports)

        # Both should be normalized to title case
        severity = report["summary"]["by_severity"]
        assert severity["High"] == 1
        assert severity["Critical"] == 1

    def test_create_report_unknown_severity(self, sample_grype_report):
        """Test handling vulnerabilities with unknown/missing severity."""
        vuln_map = {
            "CVE-2024-33333": {
                "count": 1,
                "selected_scanner": "grype",
                "vulnerability_data": {
                    "id": "CVE-2024-33333",
                    # No severity field
                },
                "related_vulnerabilities": [],
                "affected_sources": [],
                "match_details": [],
            }
        }

        reports = [sample_grype_report]
        report = create_unified_report(vuln_map, reports)

        assert report["summary"]["by_severity"]["Unknown"] == 1

    def test_create_report_multiple_images(self, sample_grype_report):
        """Test report with multiple scanned images."""
        report1 = copy.deepcopy(sample_grype_report)
        report1["_source_file"] = "image1.json"
        report1["source"]["target"]["userInput"] = "nginx:1.21"

        report2 = copy.deepcopy(sample_grype_report)
        report2["_source_file"] = "image2.json"
        report2["source"]["target"]["userInput"] = "alpine:3.18"
        report2["matches"] = []  # No matches in second image

        vuln_map = {
            "CVE-2024-12345": {
                "count": 1,
                "selected_scanner": "grype",
                "vulnerability_data": {"id": "CVE-2024-12345", "severity": "High"},
                "related_vulnerabilities": [],
                "affected_sources": [],
                "match_details": [],
            }
        }

        reports = [report1, report2]
        report = create_unified_report(vuln_map, reports)

        assert len(report["summary"]["scanned_images"]) == 2
        # Reports are processed in order
        assert report["summary"]["scanned_images"][0]["file"] == "image1.json"
        assert report["summary"]["scanned_images"][0]["image"] == "nginx:1.21"
        assert report["summary"]["scanned_images"][0]["matches"] == 1
        assert report["summary"]["scanned_images"][1]["file"] == "image2.json"
        assert report["summary"]["scanned_images"][1]["image"] == "alpine:3.18"
        assert report["summary"]["scanned_images"][1]["matches"] == 0

    def test_create_report_vulnerability_structure(self, sample_grype_report):
        """Test that vulnerability entries have correct structure."""
        vuln_map = {
            "CVE-2024-12345": {
                "count": 2,
                "selected_scanner": "grype",
                "vulnerability_data": {
                    "id": "CVE-2024-12345",
                    "severity": "High",
                    "description": "Test vuln",
                },
                "related_vulnerabilities": [{"id": "GHSA-xxxx", "namespace": "github"}],
                "affected_sources": [
                    {
                        "source_file": "report1.json",
                        "image": "nginx:1.21",
                        "artifact": {"name": "openssl", "version": "1.1.1k"},
                    }
                ],
                "match_details": [{"type": "exact"}],
            }
        }

        reports = [sample_grype_report]
        report = create_unified_report(vuln_map, reports)

        vuln = report["vulnerabilities"][0]
        assert vuln["vulnerability_id"] == "CVE-2024-12345"
        assert vuln["count"] == 2
        assert vuln["selected_scanner"] == "grype"
        assert "vulnerability" in vuln
        assert "related_vulnerabilities" in vuln
        assert "affected_sources" in vuln
        assert "match_details" in vuln

    def test_create_report_timestamp(self, vuln_map_sample, sample_grype_report):
        """Test that report includes generation timestamp."""
        reports = [sample_grype_report]
        report = create_unified_report(vuln_map_sample, reports)

        assert "generated_at" in report["metadata"]
        # Should be ISO format timestamp
        assert "T" in report["metadata"]["generated_at"]

    def test_create_report_with_package_info(self, vuln_map_sample, sample_grype_report):
        """Test that package name and version are included in metadata when provided."""
        reports = [sample_grype_report]
        report = create_unified_report(
            vuln_map_sample, reports, package_name="gitlab", package_version="18.4.2-uds.0-unicorn"
        )

        assert "package_name" in report["metadata"]
        assert report["metadata"]["package_name"] == "gitlab"
        assert "package_version" in report["metadata"]
        assert report["metadata"]["package_version"] == "18.4.2-uds.0-unicorn"

    def test_create_report_without_package_info(self, vuln_map_sample, sample_grype_report):
        """Test that package metadata fields are absent when not provided."""
        reports = [sample_grype_report]
        report = create_unified_report(vuln_map_sample, reports)

        assert "package_name" not in report["metadata"]
        assert "package_version" not in report["metadata"]

    def test_create_report_with_trivy_multiple_results(self):
        """Test Trivy report with multiple result types."""
        trivy_report = {
            "_source_file": "multi-result.json",
            "_scanner": "trivy",
            "ArtifactName": "myapp:latest",
            "SchemaVersion": "2.0.0",
            "CreatedAt": "2024-01-01T00:00:00Z",
            "Results": [
                {
                    "Type": "deb",
                    "Vulnerabilities": [
                        {
                            "VulnerabilityID": "CVE-2024-11111",
                            "Severity": "HIGH",
                        }
                    ],
                },
                {
                    "Type": "npm",
                    "Vulnerabilities": [
                        {
                            "VulnerabilityID": "CVE-2024-22222",
                            "Severity": "MEDIUM",
                        }
                    ],
                },
            ],
        }

        vuln_map = {
            "CVE-2024-11111": {
                "count": 1,
                "selected_scanner": "trivy",
                "vulnerability_data": {"id": "CVE-2024-11111", "severity": "High"},
                "related_vulnerabilities": [],
                "affected_sources": [],
                "match_details": [],
            },
            "CVE-2024-22222": {
                "count": 1,
                "selected_scanner": "trivy",
                "vulnerability_data": {"id": "CVE-2024-22222", "severity": "Medium"},
                "related_vulnerabilities": [],
                "affected_sources": [],
                "match_details": [],
            },
        }

        reports = [trivy_report]
        report = create_unified_report(vuln_map, reports)

        # Should count vulnerabilities from all result types
        scanned = report["summary"]["scanned_images"][0]
        assert scanned["matches"] == 2
