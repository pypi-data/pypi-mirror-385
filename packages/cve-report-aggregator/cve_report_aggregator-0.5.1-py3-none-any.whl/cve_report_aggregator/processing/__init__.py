"""Data processing and analysis modules for CVE Report Aggregator.

This package contains components for processing vulnerability data:
- Vulnerability aggregation and deduplication
- Scanner integration (Grype/Trivy)
- Severity scoring and selection
"""

from .aggregator import deduplicate_vulnerabilities
from .scanner import convert_to_cyclonedx, load_reports, process_trivy_reports, scan_with_trivy
from .severity import (
    extract_cvss3_scores,
    filter_null_cvss_scores,
    get_highest_cvss3_score,
    get_severity_rank,
    select_highest_severity,
)

__all__ = [
    # Aggregator
    "deduplicate_vulnerabilities",
    # Scanner
    "convert_to_cyclonedx",
    "load_reports",
    "process_trivy_reports",
    "scan_with_trivy",
    # Severity
    "extract_cvss3_scores",
    "filter_null_cvss_scores",
    "get_highest_cvss3_score",
    "get_severity_rank",
    "select_highest_severity",
]
