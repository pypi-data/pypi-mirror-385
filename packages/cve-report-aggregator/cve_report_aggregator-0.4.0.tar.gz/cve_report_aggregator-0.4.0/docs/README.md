# Documentation

This directory contains the source files for the CVE Report Aggregator documentation site, built with [MkDocs](https://www.mkdocs.org/) and the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme.

## Directory Structure

```
docs/
├── index.md                     # Home page
├── getting-started/
│   ├── installation.md         # Installation guide
│   ├── quickstart.md           # Quick start guide
│   └── docker.md               # Docker usage guide
├── configuration/
│   ├── overview.md             # Configuration overview
│   ├── quickstart.md           # Configuration quick start
│   └── implementation.md       # Implementation details
├── user-guide/
│   ├── cli.md                  # CLI reference
│   ├── scanners.md             # Scanner support
│   ├── deduplication.md        # Deduplication logic
│   └── output.md               # Output format
├── development/
│   ├── contributing.md         # Contributing guide
│   ├── architecture.md         # Architecture overview
│   └── testing.md              # Testing guide
└── reference/
    ├── api.md                  # API reference
    └── changelog.md            # Changelog
```

## Building the Documentation

### Prerequisites

```bash
# Install dependencies
uv sync
```

### Build

```bash
# Build the site
uv run mkdocs build

# The built site will be in the site/ directory
```

### Local Development

```bash
# Serve the site locally with live reload
uv run mkdocs serve

# Open http://127.0.0.1:8000 in your browser
```

### Deploy to GitHub Pages

The documentation is automatically deployed to GitHub Pages when changes are pushed to the `main` branch.

Manual deployment:

```bash
# Deploy to GitHub Pages
uv run mkdocs gh-deploy
```

## Writing Documentation

### Markdown

Documentation is written in Markdown with support for:

- [GitHub Flavored Markdown](https://github.github.com/gfm/)
- [PyMdown Extensions](https://facelessuser.github.io/pymdown-extensions/)
- [Material for MkDocs features](https://squidfunk.github.io/mkdocs-material/reference/)

### Code Blocks

Use fenced code blocks with syntax highlighting:

````markdown
```bash
cve-report-aggregator --help
```

```python
from cve_report_aggregator import config
```
````

### Admonitions

Use admonitions for notes, warnings, etc.:

```markdown
!!! note "Note Title"
    This is a note.

!!! warning "Warning"
    This is a warning.

!!! danger "Danger"
    This is a danger message.
```

### Tabs

Use tabs for alternative content:

```markdown
=== "Option 1"
    Content for option 1

=== "Option 2"
    Content for option 2
```

## Configuration

The documentation site is configured in `mkdocs.yml` at the repository root.

Key configuration sections:

- **site_name**: Documentation site name
- **theme**: Material theme configuration
- **nav**: Navigation structure
- **markdown_extensions**: Enabled Markdown extensions
- **plugins**: Enabled MkDocs plugins

## Links

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [PyMdown Extensions](https://facelessuser.github.io/pymdown-extensions/)
