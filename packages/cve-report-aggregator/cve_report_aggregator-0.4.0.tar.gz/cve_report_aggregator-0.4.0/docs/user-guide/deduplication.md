[38;2;248;248;242m# Deduplication Logic[0m

[38;2;248;248;242mCVE Report Aggregator implements intelligent deduplication across multiple scan reports to provide a unified view of vulnerabilities.[0m

[38;2;248;248;242m## Overview[0m

[38;2;248;248;242mThe deduplication engine combines identical vulnerabilities found across:[0m
[38;2;248;248;242m- Multiple container images[0m
[38;2;248;248;242m- Different scanners (Grype vs Trivy)[0m
[38;2;248;248;242m- Multiple scan runs over time[0m

[38;2;248;248;242m## CVE ID Preference Strategy[0m

[38;2;248;248;242m**Why CVE IDs are preferred over GHSA IDs:**[0m

[38;2;248;248;242m- CVE is the universal industry standard (maintained by MITRE)[0m
[38;2;248;248;242m- Consistent across different scanners (Grype, Trivy, etc.)[0m
[38;2;248;248;242m- Better cross-referencing in vulnerability databases and SBOMs[0m
[38;2;248;248;242m- Trivy natively uses CVE IDs, avoiding conversion complexity[0m

[38;2;248;248;242m**Implementation:**[0m

[38;2;248;248;242mFor Grype reports, the tool searches `relatedVulnerabilities` for CVE IDs and prefers them over GHSA IDs.[0m

[38;2;248;248;242mFor Trivy reports, CVE IDs are used directly (already in CVE-* format).[0m

[38;2;248;248;242m## Severity Selection Modes[0m

[38;2;248;248;242m### Default Mode (First-Occurrence)[0m

[38;2;248;248;242m- Uses severity from the first occurrence of each vulnerability[0m
[38;2;248;248;242m- File processing order is alphabetical by filename[0m
[38;2;248;248;242m- Preserves the exact severity rating from the primary scanner[0m

[38;2;248;248;242m### Highest-Severity Mode[0m

[38;2;248;248;242mActivated with `--mode highest-score`:[0m

[38;2;248;248;242m- Automatically selects the highest severity rating across all occurrences[0m
[38;2;248;248;242m- **Primary**: Compares CVSS 3.x base scores numerically (8.9 > 7.5)[0m
[38;2;248;248;242m- **Fallback**: If no CVSS 3.x scores, uses severity strings (Critical > High > Medium > Low > Negligible > Unknown)[0m
[38;2;248;248;242m- Ensures conservative (worst-case) severity ratings based on actual risk metrics[0m
[38;2;248;248;242m- Useful for compliance requirements[0m

[38;2;248;248;242m## Occurrence Tracking[0m

[38;2;248;248;242mEach vulnerability tracks:[0m

[38;2;248;248;242m1. **Count**: Total occurrences across all images[0m
[38;2;248;248;242m2. **Affected Sources**: Which images/packages are affected (with complete context)[0m
[38;2;248;248;242m3. **Vulnerability Data**: Full details (severity selection depends on mode)[0m
[38;2;248;248;242m4. **Match Details**: Unique matcher details aggregated from all occurrences[0m

[38;2;248;248;242m## Example[0m

[38;2;248;248;242mGiven two scans of the same image with different scanners:[0m

[38;2;248;248;242m```json[0m
[38;2;248;248;242m{[0m
[38;2;248;248;242m  "CVE-2024-12345": {[0m
[38;2;248;248;242m    "count": 2,[0m
[38;2;248;248;242m    "affected_sources": [[0m
[38;2;248;248;242m      {[0m
[38;2;248;248;242m        "source_file": "grype-scan.json",[0m
[38;2;248;248;242m        "image": "nginx:1.21",[0m
[38;2;248;248;242m        "artifact": {...}[0m
[38;2;248;248;242m      },[0m
[38;2;248;248;242m      {[0m
[38;2;248;248;242m        "source_file": "trivy-scan.json",[0m
[38;2;248;248;242m        "image": "nginx:1.21",[0m
[38;2;248;248;242m        "artifact": {...}[0m
[38;2;248;248;242m      }[0m
[38;2;248;248;242m    ],[0m
[38;2;248;248;242m    "vulnerability_data": {...},[0m
[38;2;248;248;242m    "match_details": [...][0m
[38;2;248;248;242m  }[0m
[38;2;248;248;242m}[0m
[38;2;248;248;242m```[0m

[38;2;248;248;242m## Next Steps[0m

[38;2;248;248;242m- [Output Format](output.md) - Understanding the unified report structure[0m
[38;2;248;248;242m- [Scanners](scanners.md) - Learn about supported scanners[0m
