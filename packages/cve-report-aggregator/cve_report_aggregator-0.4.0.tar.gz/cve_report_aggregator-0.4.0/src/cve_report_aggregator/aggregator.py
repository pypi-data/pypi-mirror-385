"""Core vulnerability deduplication logic."""

from collections import defaultdict
from typing import Any

from .models import ModeType
from .severity import filter_null_cvss_scores, select_highest_severity


def deduplicate_vulnerabilities(reports: list[dict[str, Any]], mode: ModeType = "highest-score") -> dict[str, Any]:
    """Deduplicates vulnerabilities across all reports.

    Groups vulnerabilities by CVE ID (or GHSA if no CVE) and tracks
    occurrence counts, affected sources, and artifact details.

    Args:
        reports: List of report dictionaries (Grype or Trivy format).
        mode: Aggregation mode - "highest-score" selects vulnerability data with highest
            CVSS 3.x score across all scanner reports, "first-occurrence" uses first
            occurrence (alphabetical order).

    Returns:
        A dictionary mapping vulnerability IDs to aggregated data including:
        count, affected_sources, vulnerability_data, related_vulnerabilities,
        and match_details.
    """
    # Track vulnerabilities by their primary ID
    vuln_map: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "count": 0,
            "affected_sources": [],
            "artifacts": [],
            "vulnerability_data": None,
            "selected_scanner": None,
            "related_vulnerabilities": [],
            "match_details": [],
        }
    )

    # Process each report
    report: dict[str, Any]
    for report in reports:
        source_name: str = report["_source_file"]
        scanner: str = report.get("_scanner", "grype")

        if scanner == "trivy":
            # Process Trivy format
            image_name: str = report.get("ArtifactName", "unknown")

            result: dict[str, Any]
            for result in report.get("Results", []):
                vuln: dict[str, Any]
                for vuln in result.get("Vulnerabilities", []):
                    vuln_id: str = vuln.get("VulnerabilityID", "")
                    if not vuln_id:
                        continue

                    # Trivy already uses CVE IDs as primary keys
                    primary_id: str = vuln_id

                    # Update vulnerability tracking
                    vuln_entry: dict[str, Any] = vuln_map[primary_id]
                    vuln_entry["count"] += 1

                    # Track source information
                    source_info: dict[str, Any] = {
                        "source_file": source_name,
                        "image": image_name,
                        "artifact": {
                            "name": vuln.get("PkgName", "unknown"),
                            "version": vuln.get("InstalledVersion", "unknown"),
                            "type": result.get("Type", "unknown"),
                            "location": vuln.get("PkgPath", None),
                        },
                    }
                    vuln_entry["affected_sources"].append(source_info)

                    # Store vulnerability data (convert to Grype-like format)
                    new_vuln_data: dict[str, Any] = {
                        "id": vuln_id,
                        "severity": vuln.get("Severity", "Unknown"),
                        "description": vuln.get("Description", ""),
                        "cvss": vuln.get("CVSS", {}),
                        "references": vuln.get("References", []),
                        "publishedDate": vuln.get("PublishedDate", ""),
                        "lastModifiedDate": vuln.get("LastModifiedDate", ""),
                    }
                    if vuln.get("FixedVersion"):
                        new_vuln_data["fix"] = {
                            "versions": [vuln["FixedVersion"]],
                            "state": "fixed",
                        }

                    # Filter out null/invalid CVSS scores
                    new_vuln_data = filter_null_cvss_scores(new_vuln_data)

                    # Select vulnerability data based on mode
                    if mode == "highest-score":
                        previous_data: dict[str, Any] | None = vuln_entry["vulnerability_data"]
                        vuln_entry["vulnerability_data"] = select_highest_severity(
                            vuln_entry["vulnerability_data"], new_vuln_data
                        )
                        # Update scanner if we selected new data
                        if vuln_entry["vulnerability_data"] != previous_data:
                            vuln_entry["selected_scanner"] = scanner
                    elif vuln_entry["vulnerability_data"] is None:
                        vuln_entry["vulnerability_data"] = new_vuln_data
                        vuln_entry["selected_scanner"] = scanner

        else:
            # Process Grype format
            image_name = report.get("source", {}).get("target", {}).get("userInput", "unknown")

            match: dict[str, Any]
            for match in report.get("matches", []):
                # Get the primary vulnerability ID (GHSA or CVE)
                vuln_id = match["vulnerability"]["id"]

                # Check related vulnerabilities for CVE IDs
                cve_ids: list[str] = []
                related: dict[str, Any]
                for related in match.get("relatedVulnerabilities", []):
                    if related["id"].startswith("CVE-"):
                        cve_ids.append(related["id"])

                # Use first CVE as primary key if available, otherwise use GHSA
                primary_id = cve_ids[0] if cve_ids else vuln_id

                # Update vulnerability tracking
                vuln_entry = vuln_map[primary_id]
                vuln_entry["count"] += 1

                # Track source information
                source_info = {
                    "source_file": source_name,
                    "image": image_name,
                    "artifact": {
                        "name": match["artifact"]["name"],
                        "version": match["artifact"]["version"],
                        "type": match["artifact"]["type"],
                        "location": (
                            match["artifact"]["locations"][0]["path"] if match["artifact"].get("locations") else None
                        ),
                    },
                }
                vuln_entry["affected_sources"].append(source_info)

                # Filter out null/invalid CVSS scores
                filtered_vuln_data: dict[str, Any] = filter_null_cvss_scores(match["vulnerability"])

                # Store vulnerability data based on mode
                if mode == "highest-score":
                    previous_data = vuln_entry["vulnerability_data"]
                    vuln_entry["vulnerability_data"] = select_highest_severity(
                        vuln_entry["vulnerability_data"], filtered_vuln_data
                    )
                    # Update related vulnerabilities and scanner if we selected new data
                    if vuln_entry["vulnerability_data"] != previous_data:
                        vuln_entry["selected_scanner"] = scanner
                        vuln_entry["related_vulnerabilities"] = match.get("relatedVulnerabilities", [])
                elif vuln_entry["vulnerability_data"] is None:
                    vuln_entry["vulnerability_data"] = filtered_vuln_data
                    vuln_entry["selected_scanner"] = scanner
                    vuln_entry["related_vulnerabilities"] = match.get("relatedVulnerabilities", [])

                # Add unique match details
                detail: dict[str, Any]
                for detail in match.get("matchDetails", []):
                    if detail not in vuln_entry["match_details"]:
                        vuln_entry["match_details"].append(detail)

    return vuln_map
