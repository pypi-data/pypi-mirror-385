"""Command-line interface for CVE Report Aggregator."""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import rich_click as click
from pydantic import ValidationError
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.pretty import Pretty
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from . import __version__
from .core.config import get_config, set_config
from .core.models import ScannerType
from .enhance.openai_client import OpenAIEnricher
from .io.csv_export import export_to_csv
from .io.downloader import download_package_sboms
from .io.report import create_executive_summary, create_unified_report
from .processing.aggregator import deduplicate_vulnerabilities
from .processing.scanner import load_reports
from .utils import ASCII_LOGO, check_command_exists, get_scanner_version

# Configure rich-click for beautiful help output
click.rich_click.USE_RICH_MARKUP = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.STYLE_ERRORS_SUGGESTION = "bold yellow"
click.rich_click.ERRORS_SUGGESTION = "Try running the '--help' flag for more information."
click.rich_click.ERRORS_EPILOGUE = ""
click.rich_click.SHOW_METAVARS_COLUMN = False
click.rich_click.APPEND_METAVARS_HELP = True
click.rich_click.OPTION_GROUPS = {
    "cve-report-aggregator": [
        {
            "name": "Configuration",
            "options": ["--config"],
        },
        {
            "name": "Input/Output Options",
            "options": ["--input-dir", "--output-file"],
        },
        {
            "name": "Scanner Configuration",
            "options": ["--scanner", "--mode"],
        },
        {
            "name": "CVE Enrichment Options",
            "options": [
                "--enrich-cves",
                "--openai-api-key",
                "--openai-model",
                "--batch-size",
                "--max-cves-to-enrich",
                "--enrich-severity-filter",
            ],
        },
        {
            "name": "Display Options",
            "options": ["--log-level"],
        },
    ],
}

# Initialize Rich console
console = Console()


def display_logo() -> None:
    """Display the ASCII logo."""
    try:
        console.print(ASCII_LOGO, style="cyan")
    except Exception:
        # Silently fall back if logo can't be displayed
        console.print("[bold cyan]🔒 CVE Report Aggregator[/bold cyan]")


@click.command(
    context_settings={"help_option_names": ["-h", "--help"]},
    epilog="🔐 [link=https://github.com/mkm29/cve-report-aggregator]https://github.com/mkm29/cve-report-aggregator[/link]",
)
@click.option(
    "-c",
    "--config",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
    default=None,
    help="Path to YAML configuration file.",
    show_default=False,
)
@click.option(
    "-i",
    "--input-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=None,
    help="Input directory containing scan report files.",
    show_default=True,
)
@click.option(
    "-o",
    "--output-file",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help="Output file path for the unified report.",
    show_default=True,
)
@click.option(
    "-s",
    "--scanner",
    type=click.Choice(["grype", "trivy"], case_sensitive=False),
    default=None,
    help="[yellow]grype[/yellow] or [yellow]trivy[/yellow] vulnerability scanner.",
    show_default=True,
)
@click.option(
    "-l",
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False),
    default=None,
    help="Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).",
    show_default=True,
)
@click.option(
    "-m",
    "--mode",
    type=click.Choice(
        ["highest-score", "first-occurrence", "grype-only", "trivy-only"],
        case_sensitive=False,
    ),
    default=None,
    help=(
        "[cyan]highest-score[/cyan]: Select highest CVSS 3.x score. "
        "[cyan]first-occurrence[/cyan]: Use first found. "
        "[cyan]grype-only[/cyan]: Grype scanner only. "
        "[cyan]trivy-only[/cyan]: Trivy scanner only."
    ),
    show_default=True,
)
@click.option(
    "--enrich-cves",
    is_flag=True,
    default=None,
    help="Enable CVE enrichment with OpenAI security context analysis.",
)
@click.option(
    "--openai-api-key",
    type=str,
    default=None,
    help="OpenAI API key (defaults to OPENAI_API_KEY env var).",
    show_default=False,
)
@click.option(
    "--openai-model",
    type=str,
    default=None,
    help="OpenAI model to use for enrichment (e.g., gpt-5-nano, gpt-4o).",
    show_default=True,
)
@click.option(
    "--batch-size",
    type=int,
    default=None,
    help="Number of CVEs to process per batch (1-100, default: 10).",
    show_default=True,
)
@click.option(
    "--max-cves-to-enrich",
    type=int,
    default=None,
    help="Maximum number of CVEs to enrich (None = all CVEs).",
    show_default=False,
)
@click.option(
    "--enrich-severity-filter",
    type=str,
    multiple=True,
    default=None,
    help=(
        "Severity levels to enrich (e.g., Critical, High). Default: Critical,High. "
        "Use multiple times for multiple severities."
    ),
    show_default=False,
)
@click.version_option(
    version=f"{__version__}",
    prog_name="CVE Report Aggregator",
    message=f"{__version__}",
)
def main(
    config: Path | None,
    input_dir: Path | None,
    output_file: Path | None,
    scanner: str | None,
    log_level: str | None,
    mode: str | None,
    enrich_cves: bool | None,
    openai_api_key: str | None,
    openai_model: str | None,
    batch_size: int | None,
    max_cves_to_enrich: int | None,
    enrich_severity_filter: tuple[str, ...] | None,
) -> None:
    """🔒 [bold cyan]CVE Report Aggregator[/bold cyan]

    Aggregate and deduplicate vulnerability scan reports from [yellow]Grype[/yellow] or [yellow]Trivy[/yellow].

    Processes vulnerability scan reports from a directory, deduplicates vulnerabilities by CVE ID,
    and generates a unified JSON report with [magenta]CVSS 3.x scoring[/magenta] and occurrence tracking.

    [bold]Configuration Priority:[/bold]
      1. CLI arguments (highest)
      2. YAML config file (--config)
      3. Environment variables (CVE_AGGREGATOR_*)
      4. Default values (lowest)

    [bold]Examples:[/bold]

      [dim]# Aggregate Grype reports with highest CVSS scores[/dim]
      [cyan]$ cve-report-aggregator -i ./reports -o unified.json[/cyan]

      [dim]# Use configuration file[/dim]
      [cyan]$ cve-report-aggregator --config ./config.yaml[/cyan]

      [dim]# Use Trivy scanner with debug logging[/dim]
      [cyan]$ cve-report-aggregator -s trivy --log-level DEBUG[/cyan]

      [dim]# Enrich CVEs with OpenAI (defaults to Critical and High severity only)[/dim]
      [cyan]$ export OPENAI_API_KEY=sk-...[/cyan]
      [cyan]$ cve-report-aggregator --enrich-cves[/cyan]

      [dim]# Enrich only top 10 CVEs with custom model[/dim]
      [cyan]$ cve-report-aggregator --enrich-cves --max-cves-to-enrich 10 --openai-model gpt-4o[/cyan]

      [dim]# Enrich all severity levels (not just Critical and High)[/dim]
      [cyan]$ cve-report-aggregator --enrich-cves --enrich-severity-filter Critical[/cyan]
      [cyan]  --enrich-severity-filter High --enrich-severity-filter Medium[/cyan]

      [dim]# First-occurrence mode (fastest)[/dim]
      [cyan]$ cve-report-aggregator -m first-occurrence[/cyan]
    """

    # Build CLI arguments dictionary (only include non-None values)
    cli_args: dict[str, Any] = {}
    if input_dir is not None:
        cli_args["input_dir"] = input_dir
    if output_file is not None:
        cli_args["output_file"] = output_file
    if scanner is not None:
        cli_args["scanner"] = scanner
    if log_level is not None:
        cli_args["log_level"] = log_level.upper()
    if mode is not None:
        cli_args["mode"] = mode

    # Build nested enrich configuration from CLI args
    enrich_config: dict[str, Any] = {}
    if enrich_cves is not None:
        enrich_config["enabled"] = enrich_cves
    if openai_api_key is not None:
        enrich_config["api_key"] = openai_api_key
    if openai_model is not None:
        enrich_config["model"] = openai_model
    if enrich_severity_filter is not None and len(enrich_severity_filter) > 0:
        enrich_config["severities"] = list(enrich_severity_filter)

    # Add enrich config to cli_args if any enrich-related options were provided
    if enrich_config:
        cli_args["enrich"] = enrich_config

    # Load configuration from all sources
    try:
        app_config = get_config(cli_args=cli_args, config_file_path=config)
    except ValidationError as e:
        console.print("[red]Error:[/red] Configuration validation failed:", style="bold red")
        for error in e.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            console.print(f"  [yellow]{field}:[/yellow] {message}", style="dim")
        sys.exit(1)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[red]Error:[/red] {e}", style="bold red")
        sys.exit(1)

    # =========================================================================
    # Initialize global configuration for sharing across modules
    # =========================================================================
    # This makes the configuration available to all modules via get_current_config()
    # without needing to pass it explicitly through every function call
    set_config(app_config)

    # Extract configuration values
    input_dir = app_config.input_dir
    output_file = app_config.output_file
    mode_value = app_config.mode
    log_level = app_config.log_level
    is_debug = log_level == "DEBUG"

    # Validate output file
    if output_file.suffix.lower() != ".json":
        console.print(
            f"[yellow]Warning:[/yellow] Output file does not have .json extension: {output_file}",
            style="dim",
        )

    # Determine effective scanner based on mode
    # Mode-specific scanners override the --scanner flag
    effective_scanner: ScannerType
    if mode_value == "grype-only":
        effective_scanner = "grype"
    elif mode_value == "trivy-only":
        effective_scanner = "trivy"
    else:
        # For highest-score and first-occurrence modes, use configured scanner
        effective_scanner = app_config.scanner

    # Validate required tools based on mode
    if mode_value == "grype-only":
        if not check_command_exists("grype"):
            console.print(
                "[red]Error:[/red] Mode 'grype-only' requires 'grype' command.\n"
                "Please install Grype: https://github.com/anchore/grype#installation",
                style="bold red",
            )
            sys.exit(1)
    elif mode_value == "trivy-only":
        if not check_command_exists("trivy"):
            console.print(
                "[red]Error:[/red] Mode 'trivy-only' requires 'trivy' command.\n"
                "Please install Trivy: https://aquasecurity.github.io/trivy/latest/getting-started/installation/",
                style="bold red",
            )
            sys.exit(1)
        if not check_command_exists("syft"):
            console.print(
                "[red]Error:[/red] Mode 'trivy-only' requires 'syft' command for SBOM conversion.\n"
                "Please install syft: https://github.com/anchore/syft#installation",
                style="bold red",
            )
            sys.exit(1)
    else:
        # For mixed modes (highest-score, first-occurrence), check scanner requirements
        if effective_scanner == "trivy":
            if not check_command_exists("syft"):
                console.print(
                    "[red]Error:[/red] Scanner 'trivy' requires 'syft' command.\n"
                    "Please install syft: https://github.com/anchore/syft#installation",
                    style="bold red",
                )
                sys.exit(1)
            if not check_command_exists("trivy"):
                console.print(
                    "[red]Error:[/red] Scanner 'trivy' requires 'trivy' command.\n"
                    "Please install Trivy: https://aquasecurity.github.io/trivy/latest/getting-started/installation/",
                    style="bold red",
                )
                sys.exit(1)
        elif effective_scanner == "grype":
            if not check_command_exists("grype"):
                console.print(
                    "[red]Error:[/red] Scanner 'grype' requires 'grype' command.\n"
                    "Please install Grype: https://github.com/anchore/grype#installation",
                    style="bold red",
                )
                sys.exit(1)

    # Validate UDS Zarf CLI if downloadRemotePackages is enabled
    if app_config.download_remote_packages:
        if not check_command_exists("uds"):
            console.print(
                "[red]Error:[/red] downloadRemotePackages requires 'uds' command.\n"
                "Please install UDS CLI: https://github.com/defenseunicorns/uds-cli",
                style="bold red",
            )
            sys.exit(1)

    # Get scanner version
    scanner_version: str = get_scanner_version(effective_scanner)

    # Display header with rich styling
    console.print()
    header_text: str = (
        f"[bold cyan]🔒 Vulnerability Report Aggregator[/bold cyan]\n"
        f"[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]\n"
        f"[bold]Mode:[/bold] [magenta]{mode_value}[/magenta]\n"
        f"[bold]Scanner:[/bold] [yellow]{effective_scanner.title()}[/yellow] [dim]v{scanner_version}[/dim]"
    )
    console.print(
        Panel(
            header_text,
            box=box.DOUBLE,
            border_style="bold cyan",
            padding=(1, 2),
        )
    )
    console.print()

    # Print configuration details if log level is DEBUG or CRITICAL
    if log_level == "DEBUG":
        console.print()
        console.print(
            Panel(
                Pretty(app_config, expand_all=True),
                title="[bold cyan]Configuration Settings[/bold cyan]",
                border_style="cyan",
                padding=(1, 2),
            )
        )
        console.print()
    elif log_level == "CRITICAL":
        console.print()
        console.print(
            Panel(
                Pretty(locals(), expand_all=True),
                title="[bold red]Local Variables (CRITICAL)[/bold red]",
                border_style="red",
                padding=(1, 2),
            )
        )
        console.print()

    # Download SBOM reports from remote registry if configured
    if app_config.download_remote_packages:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                "[cyan]Downloading SBOM reports from remote registry...",
                total=None,
            )
            try:
                downloaded_sboms = download_package_sboms(output_dir=input_dir)
                progress.update(task, completed=True)

                if is_debug and downloaded_sboms:
                    console.print(f"[green]✓[/green] Downloaded {len(downloaded_sboms)} SBOM reports\n")
            except (ValueError, RuntimeError) as e:
                progress.update(task, completed=True)
                console.print(f"[red]Error:[/red] {e}", style="bold red")
                sys.exit(1)

    # Load all reports
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"[cyan]Loading {effective_scanner} reports...", total=None)
        reports: list[dict[str, Any]] = load_reports(input_dir, scanner=effective_scanner, verbose=is_debug)
        progress.update(task, completed=True)

    if not reports:
        console.print(
            "[red]Error:[/red] No valid reports with vulnerabilities found!",
            style="bold red",
        )
        sys.exit(1)

    if is_debug:
        console.print(f"\n[green]✓[/green] Loaded {len(reports)} reports\n")

    # Group reports by package if multiple packages are configured
    reports_by_package: dict[str, list[dict[str, Any]]] = {}
    if app_config.download_remote_packages and app_config.packages:
        # Group reports by package name extracted from directory structure
        # Files are now organized as: <package-name>/<file>.json
        for report in reports:
            source_file = report.get("_source_file", "")
            # Extract package name from directory path (first component)
            # Example: "gitlab/file.json" -> "gitlab"
            path_parts = Path(source_file).parts
            if len(path_parts) > 1:
                package_name = path_parts[0]
            else:
                # Fallback: just the filename if no directory
                package_name = "unknown"

            if package_name not in reports_by_package:
                reports_by_package[package_name] = []
            reports_by_package[package_name].append(report)
    else:
        # Single unified report for all reports
        reports_by_package["unified"] = reports

    # Process each package's reports separately
    output_files_created: list[Path] = []
    all_reports: list[dict[str, Any]] = []
    all_vuln_maps: dict[str, Any] = {}

    for package_name, package_reports in reports_by_package.items():
        if is_debug:
            console.print(f"\n[cyan]Processing {len(package_reports)} reports for {package_name}...[/cyan]")

        # Find package version from configuration if available
        package_version: str | None = None
        if app_config.packages:
            for pkg in app_config.packages:
                if pkg.name == package_name:
                    package_version = pkg.version
                    break

        # Deduplicate vulnerabilities for this package
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"[cyan]Deduplicating vulnerabilities for {package_name}...", total=None)
            vuln_map: dict[str, Any] = deduplicate_vulnerabilities(package_reports, mode_value)
            progress.update(task, completed=True)

        # Create unified report for this package
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"[cyan]Creating unified report for {package_name}...", total=None)
            unified_report: dict[str, Any] = create_unified_report(
                vuln_map, package_reports, package_name=package_name, package_version=package_version
            )
            progress.update(task, completed=True)

        # Enrich CVEs with OpenAI if enabled
        if app_config.enrich.enabled:
            if not app_config.enrich.api_key:
                console.print(
                    "[yellow]Warning:[/yellow] CVE enrichment enabled but no OpenAI API key provided. "
                    "Set OPENAI_API_KEY environment variable or use --openai-api-key option.",
                    style="dim",
                )
            else:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task(
                        f"[cyan]Enriching CVEs with OpenAI for {package_name}...",
                        total=None,
                    )
                    try:
                        # Initialize OpenAI enricher with all configuration parameters
                        enricher = OpenAIEnricher(
                            api_key=app_config.enrich.api_key,
                            model=app_config.enrich.model,
                            reasoning_effort=app_config.enrich.reasoning_effort,
                            verbosity=app_config.enrich.verbosity,
                            max_completion_tokens=app_config.enrich.max_completion_tokens,
                            seed=app_config.enrich.seed,
                            metadata=app_config.enrich.metadata,
                        )

                        # Enrich vulnerabilities
                        vulnerabilities = unified_report.get("vulnerabilities", [])
                        enrichments = enricher.enrich_report(
                            vulnerabilities=vulnerabilities,
                            max_cves=None,  # No longer limiting max CVEs
                            severity_filter=app_config.enrich.severities,
                        )

                        # Add enrichments to unified report
                        unified_report["enrichments"] = {
                            cve_id: enrichment.model_dump() for cve_id, enrichment in enrichments.items()
                        }

                        # Count eligible CVEs (those matching severity filter)
                        eligible_cves = sum(
                            1
                            for vuln in vulnerabilities
                            if vuln.get("vulnerability", {}).get("severity") in app_config.enrich.severities
                        )

                        # Update summary with enrichment statistics
                        if "summary" not in unified_report:
                            unified_report["summary"] = {}
                        unified_report["summary"]["enrichment"] = {
                            "enabled": True,
                            "total_cves": len(vulnerabilities),
                            "eligible_cves": eligible_cves,
                            "enriched_cves": len(enrichments),
                            "model": app_config.enrich.model,
                            "severity_filter": app_config.enrich.severities,
                        }

                        progress.update(task, completed=True)

                        if is_debug:
                            console.print(
                                f"[green]✓[/green] Enriched {len(enrichments)} out of {len(vulnerabilities)} CVEs\n"
                            )

                    except Exception as e:
                        progress.update(task, completed=True)
                        console.print(
                            f"[yellow]Warning:[/yellow] CVE enrichment failed for {package_name}: {e}",
                            style="dim",
                        )
                        # Continue without enrichment
                        unified_report["enrichments"] = {}
                        if "summary" in unified_report:
                            vulnerabilities = unified_report.get("vulnerabilities", [])
                            eligible_cves = sum(
                                1
                                for vuln in vulnerabilities
                                if vuln.get("vulnerability", {}).get("severity") in app_config.enrich.severities
                            )
                            unified_report["summary"]["enrichment"] = {
                                "enabled": True,
                                "total_cves": len(vulnerabilities),
                                "eligible_cves": eligible_cves,
                                "enriched_cves": 0,
                                "severity_filter": app_config.enrich.severities,
                                "error": str(e),
                            }

        # Determine output file name
        # Save to $HOME/output directory
        output_dir = Path.home() / "output"

        # Use package version if available, otherwise use timestamp
        if package_version:
            # Generate output file: <package_name>-<version>.json
            package_output_file = output_dir / f"{package_name}-{package_version}.json"
        else:
            # Fallback to timestamp for backwards compatibility
            # Generate timestamp: YYYYMMDDhhmmss
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            package_output_file = output_dir / f"{package_name}-{timestamp}.json"

        # Write unified report
        package_output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(package_output_file, "w") as f:
            json.dump(unified_report, f, indent=2)

        output_files_created.append(package_output_file)

        # Generate CSV export with same base name
        csv_output_file = package_output_file.with_suffix(".csv")
        try:
            # Extract enrichments if available
            enrichments_dict = unified_report.get("enrichments", {})
            export_to_csv(unified_report, csv_output_file, enrichments=enrichments_dict)
            output_files_created.append(csv_output_file)
        except Exception as e:
            console.print(
                f"[yellow]Warning:[/yellow] CSV export failed for {package_name}: {e}",
                style="dim",
            )

        # Collect data for aggregated executive summary
        all_reports.extend(package_reports)
        # Merge vulnerability maps (keeping highest severity for duplicates across packages)
        for vuln_id, vuln_entry in vuln_map.items():
            if vuln_id not in all_vuln_maps:
                all_vuln_maps[vuln_id] = vuln_entry
            else:
                # Merge counts and affected sources
                all_vuln_maps[vuln_id]["count"] += vuln_entry["count"]
                all_vuln_maps[vuln_id]["affected_sources"].extend(vuln_entry["affected_sources"])
                all_vuln_maps[vuln_id]["match_details"].extend(vuln_entry["match_details"])

    # Create single executive summary for all packages
    if all_vuln_maps and all_reports:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Creating executive summary for all packages...", total=None)
            executive_summary: dict[str, Any] = create_executive_summary(all_vuln_maps, all_reports)
            progress.update(task, completed=True)

        # Generate timestamp for executive summary
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        # Write executive summary
        output_dir = Path.home() / "output"
        executive_summary_file = output_dir / f"executive-summary-{timestamp}.json"
        with open(executive_summary_file, "w") as f:
            json.dump(executive_summary, f, indent=2)

        output_files_created.append(executive_summary_file)

    # Display success message
    console.print()

    # Categorize output files
    unified_json = [
        f for f in output_files_created if f.suffix == ".json" and not f.name.startswith("executive-summary")
    ]
    unified_csv = [f for f in output_files_created if f.suffix == ".csv"]
    executive_summaries = [f for f in output_files_created if f.name.startswith("executive-summary")]

    if len(unified_json) == 1 and len(executive_summaries) == 1:
        # Single package - show all files
        message = "[bold green]Success![/bold green] Reports created:\n"
        message += f"  • Unified Report (JSON): [cyan]{unified_json[0].name}[/cyan]\n"
        if unified_csv:
            message += f"  • Unified Report (CSV): [cyan]{unified_csv[0].name}[/cyan]\n"
        message += f"  • Executive Summary: [cyan]{executive_summaries[0].name}[/cyan]"

        console.print(
            Panel(
                message,
                box=box.ROUNDED,
                border_style="green",
                padding=(0, 2),
            )
        )
    else:
        # Multiple packages - show all unified reports + single executive summary
        json_list = "\n".join([f"    • [cyan]{f.name}[/cyan]" for f in unified_json])
        csv_list = "\n".join([f"    • [cyan]{f.name}[/cyan]" for f in unified_csv])

        message = "[bold green]Success![/bold green] Created reports:\n\n"
        message += f"  [bold]Unified Reports (JSON):[/bold] ({len(unified_json)} packages)\n{json_list}\n\n"

        if unified_csv:
            message += f"  [bold]Unified Reports (CSV):[/bold] ({len(unified_csv)} packages)\n{csv_list}\n\n"

        if executive_summaries:
            message += f"  [bold]Executive Summary:[/bold]\n    • [cyan]{executive_summaries[0].name}[/cyan]"

        console.print(
            Panel(
                message,
                box=box.ROUNDED,
                border_style="green",
                padding=(0, 2),
            )
        )
    console.print()

    # Display summary statistics (aggregate across all packages)
    total_occurrences: int = 0
    unique_vulns: int = 0
    unique_images: set[str] = set()
    severity_breakdown: dict[str, int] = {
        "Critical": 0,
        "High": 0,
        "Medium": 0,
        "Low": 0,
        "Negligible": 0,
        "Unknown": 0,
    }
    total_enriched: int = 0
    total_eligible: int = 0
    enrichment_enabled: bool = False
    enrichment_model: str | None = None

    # Aggregate statistics from all generated reports (only unified reports, not executive summaries or CSV files)
    for output_file_path in output_files_created:
        # Skip executive summary files and CSV files - only process unified JSON reports
        if output_file_path.name.startswith("executive-summary") or output_file_path.suffix == ".csv":
            continue

        with open(output_file_path) as f:
            report_data = json.load(f)
            total_occurrences += report_data["summary"]["total_vulnerability_occurrences"]
            unique_vulns += report_data["summary"]["unique_vulnerabilities"]

            # Collect unique images from scanned_images
            for scanned_image in report_data["summary"]["scanned_images"]:
                unique_images.add(scanned_image["image"])

            for severity, count in report_data["summary"]["by_severity"].items():
                severity_breakdown[severity] = severity_breakdown.get(severity, 0) + count

            # Aggregate enrichment statistics
            if "enrichment" in report_data.get("summary", {}):
                enrichment_data = report_data["summary"]["enrichment"]
                if enrichment_data.get("enabled"):
                    enrichment_enabled = True
                    total_enriched += enrichment_data.get("enriched_cves", 0)
                    total_eligible += enrichment_data.get("eligible_cves", 0)
                    if not enrichment_model:
                        enrichment_model = enrichment_data.get("model")

    # Create summary table with enhanced styling
    table = Table(
        title="[bold cyan]📊 Executive Summary[/bold cyan]",
        box=box.DOUBLE_EDGE,
        show_header=True,
        header_style="bold magenta",
        border_style="cyan",
        title_style="bold cyan",
        padding=(0, 1),
    )
    table.add_column("Metric", style="bold cyan", no_wrap=True, width=25)
    table.add_column("Value", justify="right", style="bold yellow", width=20)

    table.add_row("Mode", f"[magenta]{mode_value}[/magenta]")
    table.add_row("Scanner", f"[yellow]{effective_scanner.title()}[/yellow]")
    table.add_row("Packages Scanned", f"[bold]{len(unified_json)}[/bold]")
    table.add_row("Images Scanned", f"[bold]{len(unique_images)}[/bold]")
    table.add_row("Total Occurrences", f"[bold]{total_occurrences}[/bold]")
    table.add_row("Unique Vulnerabilities", f"[bold green]{unique_vulns}[/bold green]")

    # Add enrichment statistics if enabled
    if enrichment_enabled:
        enrichment_pct = (total_enriched / total_eligible * 100) if total_eligible > 0 else 0
        table.add_row("", "")  # Empty separator
        table.add_row("CVE Enrichment", "[bold cyan]Enabled[/bold cyan]")
        table.add_row("Enrichment Model", f"[dim]{enrichment_model}[/dim]")
        enriched_display = f"[bold green]{total_enriched}[/bold green] / {total_eligible} ({enrichment_pct:.1f}%)"
        table.add_row("CVEs Enriched", enriched_display)

    console.print(table)
    console.print()

    # Create severity breakdown table with icons and enhanced styling
    severity_table = Table(
        title="[bold cyan]⚠️  Severity Breakdown[/bold cyan]",
        box=box.HEAVY_EDGE,
        show_header=True,
        header_style="bold magenta",
        border_style="cyan",
        title_style="bold cyan",
        padding=(0, 1),
    )
    severity_table.add_column("Severity", style="bold", no_wrap=True, width=15)
    severity_table.add_column("Count", justify="right", width=10)
    severity_table.add_column("Bar", width=30)

    # Color-code severity levels with icons
    severity_config: dict[str, dict[str, str]] = {
        "Critical": {"color": "bold red", "icon": "🔴"},
        "High": {"color": "red", "icon": "🟠"},
        "Medium": {"color": "yellow", "icon": "🟡"},
        "Low": {"color": "blue", "icon": "🔵"},
        "Negligible": {"color": "dim", "icon": "⚪"},
        "Unknown": {"color": "dim", "icon": "❓"},
    }

    # Calculate max count for bar chart
    max_count: int = max(severity_breakdown.values()) if severity_breakdown.values() else 1

    severity_order: list[str] = ["Critical", "High", "Medium", "Low", "Negligible", "Unknown"]
    for severity in severity_order:
        count = severity_breakdown.get(severity, 0)
        config_item: dict[str, str] = severity_config.get(severity, {"color": "white", "icon": "⚫"})
        color: str = config_item["color"]
        icon: str = config_item["icon"]

        # Create bar chart
        bar_length: int = int((count / max_count) * 20) if max_count > 0 and count > 0 else 0
        bar: str = "█" * bar_length

        severity_table.add_row(
            f"{icon} [{color}]{severity}[/{color}]",
            f"[{color}]{count}[/{color}]",
            f"[{color}]{bar}[/{color}]",
        )

    console.print(severity_table)
    console.print()
