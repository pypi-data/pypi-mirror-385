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
from .io.downloader import download_package_sboms
from .io.report import create_unified_report
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

      [dim]# Set specific log level[/dim]
      [cyan]$ cve-report-aggregator --log-level DEBUG[/cyan]

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

    for package_name, package_reports in reports_by_package.items():
        if is_debug:
            console.print(f"\n[cyan]Processing {len(package_reports)} reports for {package_name}...[/cyan]")

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
            unified_report: dict[str, Any] = create_unified_report(vuln_map, package_reports)
            progress.update(task, completed=True)

        # Determine output file name with timestamp
        # Generate timestamp: YYYYMMDDhhmmss
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        # Generate output file with timestamp: <package_name>-<timestamp>.json
        # Save to $HOME/output directory
        output_dir = Path.home() / "output"
        package_output_file = output_dir / f"{package_name}-{timestamp}.json"

        # Write output
        package_output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(package_output_file, "w") as f:
            json.dump(unified_report, f, indent=2)

        output_files_created.append(package_output_file)

    # Display success message
    console.print()
    if len(output_files_created) == 1:
        console.print(
            Panel(
                f"[bold green]Success![/bold green] Unified report created\n[cyan]{output_files_created[0]}[/cyan]",
                box=box.ROUNDED,
                border_style="green",
                padding=(0, 2),
            )
        )
    else:
        files_list = "\n".join([f"  • [cyan]{f.name}[/cyan]" for f in output_files_created])
        console.print(
            Panel(
                f"[bold green]Success![/bold green] Created {len(output_files_created)} unified reports:\n{files_list}",
                box=box.ROUNDED,
                border_style="green",
                padding=(0, 2),
            )
        )
    console.print()

    # Display summary statistics (aggregate across all packages)
    total_occurrences: int = 0
    unique_vulns: int = 0
    severity_breakdown: dict[str, int] = {
        "Critical": 0,
        "High": 0,
        "Medium": 0,
        "Low": 0,
        "Negligible": 0,
        "Unknown": 0,
    }

    # Aggregate statistics from all generated reports
    for output_file_path in output_files_created:
        with open(output_file_path) as f:
            report_data = json.load(f)
            total_occurrences += report_data["summary"]["total_vulnerability_occurrences"]
            unique_vulns += report_data["summary"]["unique_vulnerabilities"]
            for severity, count in report_data["summary"]["by_severity"].items():
                severity_breakdown[severity] = severity_breakdown.get(severity, 0) + count

    # Create summary table with enhanced styling
    table = Table(
        title="[bold cyan]📊 Vulnerability Summary[/bold cyan]",
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
    table.add_row("Total Occurrences", f"[bold]{total_occurrences}[/bold]")
    table.add_row("Unique Vulnerabilities", f"[bold green]{unique_vulns}[/bold green]")

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
