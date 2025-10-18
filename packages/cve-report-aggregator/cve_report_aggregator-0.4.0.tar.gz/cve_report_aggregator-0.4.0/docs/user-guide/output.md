[38;2;248;248;242m# Output Format[0m

[38;2;248;248;242mThe unified report provides a comprehensive view of all vulnerabilities found across scanned images.[0m

[38;2;248;248;242m## Report Structure[0m

[38;2;248;248;242m### Metadata Section[0m

[38;2;248;248;242m- Generation timestamp[0m
[38;2;248;248;242m- Scanner type and version[0m
[38;2;248;248;242m- Source report count and filenames[0m

[38;2;248;248;242m### Summary Section[0m

[38;2;248;248;242m- Total vulnerability occurrences (count across all images)[0m
[38;2;248;248;242m- Unique vulnerability count (deduplicated)[0m
[38;2;248;248;242m- Severity breakdown (Critical, High, Medium, Low, Negligible, Unknown)[0m
[38;2;248;248;242m- Per-image scan results with match counts[0m

[38;2;248;248;242m### Vulnerabilities Section (Deduplicated)[0m

[38;2;248;248;242mEach entry includes:[0m

[38;2;248;248;242m- **Vulnerability ID**: CVE or GHSA identifier[0m
[38;2;248;248;242m- **Occurrence count**: How many times found across all images[0m
[38;2;248;248;242m- **Selected scanner**: Which scanner provided the vulnerability data[0m
[38;2;248;248;242m- **Full vulnerability data**: Severity, CVSS, description, fix versions[0m
[38;2;248;248;242m- **Related vulnerabilities**: GHSA cross-references for CVE entries[0m
[38;2;248;248;242m- **Affected sources**: All images/packages where vulnerability was found[0m
[38;2;248;248;242m- **Match details**: Unique matcher information from all occurrences[0m

[38;2;248;248;242m### Database Info Section[0m

[38;2;248;248;242mScanner-specific metadata:[0m

[38;2;248;248;242m- **Grype**: `descriptor.db` with build timestamp and schema version[0m
[38;2;248;248;242m- **Trivy**: `SchemaVersion` and `CreatedAt` timestamp[0m

[38;2;248;248;242m## Example Output[0m

[38;2;248;248;242m```json[0m
[38;2;248;248;242m{[0m
[38;2;248;248;242m  "metadata": {[0m
[38;2;248;248;242m    "generated_at": "2025-01-17T12:00:00Z",[0m
[38;2;248;248;242m    "scanner": "grype",[0m
[38;2;248;248;242m    "scanner_version": "0.100.0",[0m
[38;2;248;248;242m    "source_reports": ["service1.json", "service2.json"][0m
[38;2;248;248;242m  },[0m
[38;2;248;248;242m  "summary": {[0m
[38;2;248;248;242m    "total_occurrences": 150,[0m
[38;2;248;248;242m    "unique_vulnerabilities": 75,[0m
[38;2;248;248;242m    "by_severity": {[0m
[38;2;248;248;242m      "Critical": 5,[0m
[38;2;248;248;242m      "High": 20,[0m
[38;2;248;248;242m      "Medium": 30,[0m
[38;2;248;248;242m      "Low": 15,[0m
[38;2;248;248;242m      "Negligible": 5[0m
[38;2;248;248;242m    },[0m
[38;2;248;248;242m    "by_image": [[0m
[38;2;248;248;242m      {[0m
[38;2;248;248;242m        "image": "nginx:1.21",[0m
[38;2;248;248;242m        "matches": 50[0m
[38;2;248;248;242m      }[0m
[38;2;248;248;242m    ][0m
[38;2;248;248;242m  },[0m
[38;2;248;248;242m  "vulnerabilities": [[0m
[38;2;248;248;242m    {[0m
[38;2;248;248;242m      "id": "CVE-2024-12345",[0m
[38;2;248;248;242m      "count": 2,[0m
[38;2;248;248;242m      "scanner": "grype",[0m
[38;2;248;248;242m      "vulnerability": {...},[0m
[38;2;248;248;242m      "affected_sources": [...],[0m
[38;2;248;248;242m      "match_details": [...][0m
[38;2;248;248;242m    }[0m
[38;2;248;248;242m  ],[0m
[38;2;248;248;242m  "database_info": {...}[0m
[38;2;248;248;242m}[0m
[38;2;248;248;242m```[0m

[38;2;248;248;242m## Querying Results[0m

[38;2;248;248;242mUse `jq` to query the unified report:[0m

[38;2;248;248;242m```bash[0m
[38;2;248;248;242m# View summary[0m
[38;2;248;248;242mjq '.summary' unified-report.json[0m

[38;2;248;248;242m# Filter by severity[0m
[38;2;248;248;242mjq '.vulnerabilities[] | select(.vulnerability.severity == "Critical")' unified-report.json[0m

[38;2;248;248;242m# Count by severity[0m
[38;2;248;248;242mjq '.summary.by_severity' unified-report.json[0m

[38;2;248;248;242m# List affected images for a CVE[0m
[38;2;248;248;242mjq '.vulnerabilities[] | select(.id == "CVE-2024-12345") | .affected_sources' unified-report.json[0m
[38;2;248;248;242m```[0m

[38;2;248;248;242m## Next Steps[0m

[38;2;248;248;242m- [CLI Reference](cli.md) - Full command-line options[0m
[38;2;248;248;242m- [Deduplication](deduplication.md) - Learn about deduplication logic[0m
