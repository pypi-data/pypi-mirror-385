"""Data models and type definitions for CVE report aggregation."""

from typing import Literal

# Type aliases for better type hints
ScannerType = Literal["grype", "trivy"]
ModeType = Literal["highest-score", "first-occurrence", "grype-only", "trivy-only"]
