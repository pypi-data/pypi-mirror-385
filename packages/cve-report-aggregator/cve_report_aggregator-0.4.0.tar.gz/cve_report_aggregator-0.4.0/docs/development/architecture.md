[38;2;248;248;242m# Architecture[0m

[38;2;248;248;242mOverview of the CVE Report Aggregator architecture and design patterns.[0m

[38;2;248;248;242m## Code Organization[0m

[38;2;248;248;242mThe codebase is organized into clear functional modules:[0m

[38;2;248;248;242m1. **Configuration & Validation** (`config.py`, `models.py`): Pydantic models with validators[0m
[38;2;248;248;242m2. **Tool Utilities** (`utils.py`): Command existence checks, version detection[0m
[38;2;248;248;242m3. **Scanner Integration** (`scanner.py`): CycloneDX conversion, Trivy/Grype scanning[0m
[38;2;248;248;242m4. **Report Loading** (`scanner.py`): JSON parsing, SBOM detection[0m
[38;2;248;248;242m5. **Severity Utilities** (`severity.py`): Severity ranking, CVSS extraction[0m
[38;2;248;248;242m6. **Deduplication Engine** (`aggregator.py`): CVE normalization, occurrence tracking[0m
[38;2;248;248;242m7. **Report Generation** (`report.py`): Unified report structure creation[0m
[38;2;248;248;242m8. **CLI & Output** (`cli.py`): Argument parsing, Rich terminal output[0m

[38;2;248;248;242m## Key Design Patterns[0m

[38;2;248;248;242m### Pydantic Settings[0m

[38;2;248;248;242mConfiguration management uses Pydantic Settings with multiple sources:[0m

[38;2;248;248;242m- CLI arguments (highest priority)[0m
[38;2;248;248;242m- YAML configuration files[0m
[38;2;248;248;242m- Environment variables[0m
[38;2;248;248;242m- Default values (lowest priority)[0m

[38;2;248;248;242m### Deduplication Strategy[0m

[38;2;248;248;242mUses dictionary-based tracking for O(1) lookups:[0m

[38;2;248;248;242m```python[0m
[38;2;248;248;242mvuln_map = {[0m
[38;2;248;248;242m    "CVE-2024-12345": {[0m
[38;2;248;248;242m        "count": 3,[0m
[38;2;248;248;242m        "affected_sources": [...],[0m
[38;2;248;248;242m        "vulnerability_data": {...},[0m
[38;2;248;248;242m        "match_details": [...][0m
[38;2;248;248;242m    }[0m
[38;2;248;248;242m}[0m
[38;2;248;248;242m```[0m

[38;2;248;248;242m### Type Safety[0m

[38;2;248;248;242mFull type hints with mypy strict mode validation throughout the codebase.[0m

[38;2;248;248;242m## Performance Characteristics[0m

[38;2;248;248;242m- **Memory Efficient**: Uses `defaultdict` to avoid repeated key existence checks[0m
[38;2;248;248;242m- **Linear Complexity**: Single pass through all reports, O(n) where n = total vulnerabilities[0m
[38;2;248;248;242m- **Hash-Based Lookups**: Dictionary-based vulnerability tracking for O(1) access[0m
[38;2;248;248;242m- **Minimal Duplication**: Stores full vulnerability data only once per unique CVE[0m

[38;2;248;248;242m## Next Steps[0m

[38;2;248;248;242m- [Testing Guide](testing.md) - Learn about the test suite[0m
[38;2;248;248;242m- [Contributing](contributing.md) - Contribute to the project[0m
