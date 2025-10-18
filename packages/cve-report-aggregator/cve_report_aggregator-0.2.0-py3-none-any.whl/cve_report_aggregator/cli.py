"""Command-line interface for CVE Report Aggregator."""

import json
import sys
from pathlib import Path
from typing import Any

import rich_click as click
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from . import __version__
from .aggregator import deduplicate_vulnerabilities
from .models import ScannerType
from .report import create_unified_report
from .scanner import load_reports
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
            "name": "Input/Output Options",
            "options": ["--input-dir", "--output-file"],
        },
        {
            "name": "Scanner Configuration",
            "options": ["--scanner", "--mode"],
        },
        {
            "name": "Display Options",
            "options": ["--verbose"],
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
    epilog="💜 [link=https://github.com/mkm29/cve-report-aggregator]https://github.com/mkm29/cve-report-aggregator[/link]",
)
@click.option(
    "-i",
    "--input-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=Path.cwd() / "reports",
    help="Input directory containing scan report files.",
    show_default=True,
)
@click.option(
    "-o",
    "--output-file",
    type=click.Path(dir_okay=False, path_type=Path),
    default=Path.cwd() / "unified-report.json",
    help="Output file path for the unified report.",
    show_default=True,
)
@click.option(
    "-s",
    "--scanner",
    type=click.Choice(["grype", "trivy"], case_sensitive=False),
    default="grype",
    help="[yellow]grype[/yellow] or [yellow]trivy[/yellow] vulnerability scanner.",
    show_default=True,
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output with detailed processing information.",
)
@click.option(
    "-m",
    "--mode",
    type=click.Choice(
        ["highest-score", "first-occurrence", "grype-only", "trivy-only"],
        case_sensitive=False,
    ),
    default="highest-score",
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
    input_dir: Path,
    output_file: Path,
    scanner: str,
    verbose: bool,
    mode: str,
) -> None:
    """🔒 [bold cyan]CVE Report Aggregator[/bold cyan]

    Aggregate and deduplicate vulnerability scan reports from [yellow]Grype[/yellow] or [yellow]Trivy[/yellow].

    Processes vulnerability scan reports from a directory, deduplicates vulnerabilities by CVE ID,
    and generates a unified JSON report with [magenta]CVSS 3.x scoring[/magenta] and occurrence tracking.

    [bold]Examples:[/bold]

      [dim]# Aggregate Grype reports with highest CVSS scores[/dim]
      [cyan]$ cve-report-aggregator -i ./reports -o unified.json[/cyan]

      [dim]# Use Trivy scanner with verbose output[/dim]
      [cyan]$ cve-report-aggregator -s trivy -v[/cyan]

      [dim]# First-occurrence mode (fastest)[/dim]
      [cyan]$ cve-report-aggregator -m first-occurrence[/cyan]
    """

    # Validate output file
    output_file = output_file.resolve()
    if not output_file.parent.exists():
        console.print(
            f"[red]Error:[/red] Output file parent directory does not exist: {output_file.parent}",
            style="bold red",
        )
        sys.exit(1)

    if output_file.exists() and output_file.is_dir():
        console.print(
            f"[red]Error:[/red] Output path is a directory, not a file: {output_file}",
            style="bold red",
        )
        sys.exit(1)

    if output_file.suffix.lower() != ".json":
        console.print(
            f"[yellow]Warning:[/yellow] Output file does not have .json extension: {output_file}",
            style="dim",
        )

    # Determine effective scanner based on mode
    # Mode-specific scanners override the --scanner flag
    effective_scanner: ScannerType
    if mode == "grype-only":
        effective_scanner = "grype"  # type: ignore[assignment]
    elif mode == "trivy-only":
        effective_scanner = "trivy"  # type: ignore[assignment]
    else:
        # For highest-score and first-occurrence modes, use configured scanner
        effective_scanner = scanner  # type: ignore

    # Validate required tools based on mode
    if mode == "grype-only":
        if not check_command_exists("grype"):
            console.print(
                "[red]Error:[/red] Mode 'grype-only' requires 'grype' command.\n"
                "Please install Grype: https://github.com/anchore/grype#installation",
                style="bold red",
            )
            sys.exit(1)
    elif mode == "trivy-only":
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

    # Get scanner version
    scanner_version: str = get_scanner_version(effective_scanner)

    # Display header with rich styling
    console.print()
    header_text: str = (
        f"[bold cyan]🔒 Vulnerability Report Aggregator[/bold cyan]\n"
        f"[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]\n"
        f"[bold]Mode:[/bold] [magenta]{mode}[/magenta]\n"
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

    if verbose:
        console.print(f"[dim]Reports directory: {input_dir}[/dim]")
        console.print(f"[dim]Mode: {mode}[/dim]")
        console.print()

    # Load all reports
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"[cyan]Loading {effective_scanner} reports...", total=None)
        reports: list[dict[str, Any]] = load_reports(input_dir, scanner=effective_scanner, verbose=verbose)
        progress.update(task, completed=True)

    if not reports:
        console.print(
            "[red]Error:[/red] No valid reports with vulnerabilities found!",
            style="bold red",
        )
        sys.exit(1)

    if verbose:
        console.print(f"\n[green]✓[/green] Loaded {len(reports)} reports\n")

    # Deduplicate vulnerabilities
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Deduplicating vulnerabilities...", total=None)
        vuln_map: dict[str, Any] = deduplicate_vulnerabilities(reports, mode)  # type: ignore[arg-type]
        progress.update(task, completed=True)

    # Create unified report
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Creating unified report...", total=None)
        unified_report: dict[str, Any] = create_unified_report(vuln_map, reports)
        progress.update(task, completed=True)

    # Write output
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(unified_report, f, indent=2)

    console.print()
    console.print(
        Panel(
            f"[bold green]✓ Success![/bold green] Unified report created\n[cyan]{output_file}[/cyan]",
            box=box.ROUNDED,
            border_style="green",
            padding=(0, 2),
        )
    )
    console.print()

    # Display summary statistics
    total_occurrences: int = unified_report["summary"]["total_vulnerability_occurrences"]
    unique_vulns: int = unified_report["summary"]["unique_vulnerabilities"]
    severity_breakdown: dict[str, int] = unified_report["summary"]["by_severity"]

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

    table.add_row("Mode", f"[magenta]{mode}[/magenta]")
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
    severity: str
    for severity in severity_order:
        count: int = severity_breakdown.get(severity, 0)
        config: dict[str, str] = severity_config.get(severity, {"color": "white", "icon": "⚫"})
        color: str = config["color"]
        icon: str = config["icon"]

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
