"""Report generation for unified vulnerability data."""

from datetime import datetime
from typing import Any


def create_unified_report(vuln_map: dict[str, Any], reports: list[dict[str, Any]]) -> dict[str, Any]:
    """Creates a unified report structure with aggregated vulnerability data.

    Args:
        vuln_map: Dictionary mapping vulnerability IDs to aggregated
            vulnerability data.
        reports: List of original report dictionaries.

    Returns:
        A dictionary containing the complete unified report with metadata,
        summary statistics, vulnerability details, and database information.
    """
    # Get metadata from the first report
    first_report: dict[str, Any] = reports[0] if reports else {}
    scanner: str = first_report.get("_scanner", "grype")

    # Calculate statistics
    total_matches: int = sum(entry["count"] for entry in vuln_map.values())
    unique_vulnerabilities: int = len(vuln_map)

    # Initialize all severity levels with 0
    severity_counts: dict[str, int] = {
        "Critical": 0,
        "High": 0,
        "Medium": 0,
        "Low": 0,
        "Negligible": 0,
        "Unknown": 0,
    }

    # Group by severity
    _vuln_id: str
    entry: dict[str, Any]
    for _vuln_id, entry in vuln_map.items():
        severity: str = entry["vulnerability_data"].get("severity", "Unknown")
        # Handle case variations (Trivy uses uppercase, Grype uses title case)
        severity_normalized: str = severity.title() if severity else "Unknown"
        if severity_normalized not in severity_counts:
            severity_counts[severity_normalized] = 0
        severity_counts[severity_normalized] += entry["count"]

    # Create unified matches list
    unified_matches: list[dict[str, Any]] = []
    vuln_id: str
    for vuln_id, entry in sorted(vuln_map.items(), key=lambda x: x[1]["count"], reverse=True):
        unified_match: dict[str, Any] = {
            "vulnerability_id": vuln_id,
            "count": entry["count"],
            "vulnerability": entry["vulnerability_data"],
            "selected_scanner": entry["selected_scanner"],
            "related_vulnerabilities": entry["related_vulnerabilities"],
            "affected_sources": entry["affected_sources"],
            "match_details": entry["match_details"],
        }
        unified_matches.append(unified_match)

    # Build scanner-specific metadata
    if scanner == "trivy":
        scanner_version: str = first_report.get("SchemaVersion", "unknown")
        scanned_images: list[dict[str, Any]] = [
            {
                "file": r["_source_file"],
                "image": r.get("ArtifactName", "unknown"),
                "matches": sum(len(result.get("Vulnerabilities", [])) for result in r.get("Results", [])),
            }
            for r in reports
        ]
        db_info: dict[str, Any] = {
            "schema_version": first_report.get("SchemaVersion", ""),
            "created_at": first_report.get("CreatedAt", ""),
        }
    else:
        scanner_version = first_report.get("descriptor", {}).get("version", "unknown")
        scanned_images = [
            {
                "file": r["_source_file"],
                "image": (r.get("source", {}).get("target", {}).get("userInput", "unknown")),
                "matches": len(r.get("matches", [])),
            }
            for r in reports
        ]
        db_info = first_report.get("descriptor", {}).get("db", {})

    # Build unified report
    unified_report: dict[str, Any] = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "scanner": scanner,
            "scanner_version": scanner_version,
            "source_reports_count": len(reports),
            "source_reports": [r["_source_file"] for r in reports],
        },
        "summary": {
            "total_vulnerability_occurrences": total_matches,
            "unique_vulnerabilities": unique_vulnerabilities,
            "by_severity": severity_counts,
            "scanned_images": scanned_images,
        },
        "vulnerabilities": unified_matches,
        "database_info": db_info,
    }

    return unified_report
