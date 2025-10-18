[38;2;248;248;242m# Testing Guide[0m

[38;2;248;248;242mCVE Report Aggregator has a comprehensive test suite to ensure reliability and correctness.[0m

[38;2;248;248;242m## Running Tests[0m

[38;2;248;248;242m```bash[0m
[38;2;248;248;242m# Run all tests[0m
[38;2;248;248;242muv run pytest[0m

[38;2;248;248;242m# Run with coverage[0m
[38;2;248;248;242muv run pytest --cov=cve_report_aggregator --cov-report=html[0m

[38;2;248;248;242m# Run specific test file[0m
[38;2;248;248;242muv run pytest tests/unit/test_severity.py[0m

[38;2;248;248;242m# Run verbose[0m
[38;2;248;248;242muv run pytest -v[0m

[38;2;248;248;242m# Run with short traceback[0m
[38;2;248;248;242muv run pytest --tb=short[0m
[38;2;248;248;242m```[0m

[38;2;248;248;242m## Test Organization[0m

[38;2;248;248;242m```[0m
[38;2;248;248;242mtests/[0m
[38;2;248;248;242m├── unit/[0m
[38;2;248;248;242m│   ├── test_config.py        # Configuration tests[0m
[38;2;248;248;242m│   ├── test_aggregator.py    # Deduplication tests[0m
[38;2;248;248;242m│   ├── test_severity.py      # CVSS and severity tests[0m
[38;2;248;248;242m│   ├── test_scanner.py       # Scanner integration tests[0m
[38;2;248;248;242m│   └── test_report.py        # Report generation tests[0m
[38;2;248;248;242m└── conftest.py               # Shared fixtures[0m
[38;2;248;248;242m```[0m

[38;2;248;248;242m## Test Coverage[0m

[38;2;248;248;242mThe project maintains high test coverage:[0m

[38;2;248;248;242m- **config.py**: 96%[0m
[38;2;248;248;242m- **models.py**: 82%[0m
[38;2;248;248;242m- **Overall**: Target 80%+[0m

[38;2;248;248;242m## Writing Tests[0m

[38;2;248;248;242m### Using Fixtures[0m

[38;2;248;248;242m```python[0m
[38;2;248;248;242mdef test_with_temp_dir(tmp_path):[0m
[38;2;248;248;242m    """Use pytest's tmp_path fixture for temp directories."""[0m
[38;2;248;248;242m    report_dir = tmp_path / "reports"[0m
[38;2;248;248;242m    report_dir.mkdir()[0m
[38;2;248;248;242m    # ...[0m
[38;2;248;248;242m```[0m

[38;2;248;248;242m### Mocking Subprocess[0m

[38;2;248;248;242m```python[0m
[38;2;248;248;242mdef test_scanner(monkeypatch):[0m
[38;2;248;248;242m    """Mock subprocess calls."""[0m
[38;2;248;248;242m    def mock_run(*args, **kwargs):[0m
[38;2;248;248;242m        class MockResult:[0m
[38;2;248;248;242m            stdout = json.dumps({"matches": []})[0m
[38;2;248;248;242m            returncode = 0[0m
[38;2;248;248;242m        return MockResult()[0m
[38;2;248;248;242m    [0m
[38;2;248;248;242m    monkeypatch.setattr(subprocess, "run", mock_run)[0m
[38;2;248;248;242m    # ...[0m
[38;2;248;248;242m```[0m

[38;2;248;248;242m## Code Quality[0m

[38;2;248;248;242m```bash[0m
[38;2;248;248;242m# Format code[0m
[38;2;248;248;242muv run ruff format src/ tests/[0m

[38;2;248;248;242m# Lint code[0m
[38;2;248;248;242muv run ruff check src/ tests/[0m

[38;2;248;248;242m# Type checking[0m
[38;2;248;248;242muv run mypy src/ --strict[0m
[38;2;248;248;242m```[0m

[38;2;248;248;242m## Next Steps[0m

[38;2;248;248;242m- [Architecture](architecture.md) - Learn about the codebase structure[0m
[38;2;248;248;242m- [Contributing](contributing.md) - Contribute to the project[0m
