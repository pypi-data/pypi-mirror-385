"""Scanner integration for Grype and Trivy vulnerability scanners."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from rich.console import Console

from .models import ScannerType

console = Console()


def convert_to_cyclonedx(grype_report: Path, output_dir: Path, verbose: bool = False) -> Path:
    """Convert Grype report to CycloneDX format using Syft.

    Args:
        grype_report: Path to the Grype JSON report.
        output_dir: Directory to store the converted file.
        verbose: Whether to print conversion details.

    Returns:
        Path to the converted CycloneDX JSON file.
    """
    cdx_file: Path = output_dir / f"{grype_report.stem}.cdx.json"

    if verbose:
        console.print(
            f"[cyan]Converting[/cyan] {grype_report.name} to CycloneDX...",
            style="dim",
        )

    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            ["syft", "convert", str(grype_report), "-o", "cyclonedx-json"],
            check=True,
            capture_output=True,
            text=True,
        )
        cdx_file.write_text(result.stdout)

        if verbose:
            console.print(f"  [green]✓[/green] Created: {cdx_file.name}", style="dim")

        return cdx_file
    except subprocess.CalledProcessError as e:
        console.print(
            f"[red]Error[/red] converting {grype_report.name} to CycloneDX: {e.stderr}",
            style="bold red",
        )
        raise
    except FileNotFoundError:
        console.print(
            "[red]Error:[/red] 'syft' command not found. Please install syft to use Trivy scanning.",
            style="bold red",
        )
        sys.exit(1)


def scan_with_trivy(cdx_file: Path, output_dir: Path, verbose: bool = False) -> Path:
    """Scan CycloneDX SBOM with Trivy.

    Args:
        cdx_file: Path to the CycloneDX JSON file.
        output_dir: Directory to store the Trivy report.
        verbose: Whether to print scanning details.

    Returns:
        Path to the Trivy JSON report.
    """
    trivy_report: Path = output_dir / f"{cdx_file.stem.replace('.cdx', '')}.trivy.json"

    if verbose:
        console.print(f"[cyan]Scanning[/cyan] {cdx_file.name} with Trivy...", style="dim")

    try:
        subprocess.run(
            ["trivy", "sbom", str(cdx_file), "-f", "json", "-o", str(trivy_report)],
            check=True,
            capture_output=True,
            text=True,
        )

        if verbose:
            console.print(f"  [green]✓[/green] Created: {trivy_report.name}", style="dim")

        return trivy_report
    except subprocess.CalledProcessError as e:
        console.print(
            f"[red]Error[/red] scanning {cdx_file.name} with Trivy: {e}",
            style="bold red",
        )
        raise
    except FileNotFoundError:
        console.print(
            "[red]Error:[/red] 'trivy' command not found. Please install Trivy.",
            style="bold red",
        )
        sys.exit(1)


def process_trivy_reports(reports_dir: Path, verbose: bool = False) -> list[dict[str, Any]]:
    """Convert Grype reports to CycloneDX and scan with Trivy.

    Args:
        reports_dir: Directory containing Grype JSON reports.
        verbose: Whether to print detailed processing information.

    Returns:
        List of Trivy report dictionaries.
    """
    # Create temporary directory for intermediate files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path: Path = Path(temp_dir)
        trivy_reports: list[dict[str, Any]] = []

        json_files: list[Path] = list(reports_dir.glob("*.json"))
        if not json_files:
            console.print(
                f"[red]Error:[/red] No JSON files found in '{reports_dir}'.",
                style="bold red",
            )
            sys.exit(1)

        grype_report: Path
        for grype_report in json_files:
            try:
                # Convert to CycloneDX
                cdx_file: Path = convert_to_cyclonedx(grype_report, temp_path, verbose)

                # Scan with Trivy
                trivy_report_path: Path = scan_with_trivy(cdx_file, temp_path, verbose)

                # Load the Trivy report
                with open(trivy_report_path) as f:
                    data: dict[str, Any] = json.load(f)
                    data["_source_file"] = grype_report.name
                    data["_scanner"] = "trivy"
                    trivy_reports.append(data)

            except Exception as e:
                console.print(
                    f"[red]Error[/red] processing {grype_report.name}: {e}",
                    style="bold red",
                )
                continue

        return trivy_reports


def load_reports(reports_dir: Path, scanner: ScannerType = "grype", verbose: bool = False) -> list[dict[str, Any]]:
    """Loads all JSON report files from the specified directory.

    Args:
        reports_dir: Path object pointing to the directory containing JSON
            report files.
        scanner: Type of scanner ("grype" or "trivy").
        verbose: Whether to print detailed loading information.

    Returns:
        A list of dictionaries, each representing a loaded scan report.
        Only reports with vulnerability matches are included.
    """
    # For Trivy, convert and scan first
    if scanner == "trivy":
        return process_trivy_reports(reports_dir, verbose)

    # For Grype, load reports directly
    reports: list[dict[str, Any]] = []
    json_files: list[Path] = list(reports_dir.glob("*.json"))
    if not json_files:
        console.print(
            f"[red]Error:[/red] No JSON files found in '{reports_dir}'.",
            style="bold red",
        )
        sys.exit(1)

    report_file: Path
    for report_file in json_files:
        try:
            with open(report_file) as f:
                data: dict[str, Any] = json.load(f)

                # Check if this is a Grype scan result (has "matches" field)
                if data.get("matches"):
                    data["_source_file"] = report_file.name
                    data["_scanner"] = "grype"
                    reports.append(data)
                    if verbose:
                        match_count: int = len(data.get("matches", []))
                        console.print(
                            f"[green]✓[/green] Loaded: {report_file.name} ([cyan]{match_count}[/cyan] matches)",
                            style="dim",
                        )
                # Check if this is a Syft SBOM (has "artifacts" and "descriptor" fields)
                elif data.get("artifacts") and data.get("descriptor"):
                    if verbose:
                        console.print(
                            f"[cyan]Scanning SBOM[/cyan] {report_file.name} with Grype...",
                            style="dim",
                        )

                    # Scan the SBOM with Grype
                    try:
                        result: subprocess.CompletedProcess[str] = subprocess.run(
                            ["grype", f"sbom:{report_file}", "-o", "json"],
                            check=True,
                            capture_output=True,
                            text=True,
                        )
                        scan_data: dict[str, Any] = json.loads(result.stdout)

                        if scan_data.get("matches"):
                            scan_data["_source_file"] = report_file.name
                            scan_data["_scanner"] = "grype"
                            reports.append(scan_data)
                            if verbose:
                                match_count = len(scan_data.get("matches", []))
                                console.print(
                                    f"  [green]✓[/green] Scanned: {report_file.name} "
                                    f"([cyan]{match_count}[/cyan] vulnerabilities)",
                                    style="dim",
                                )
                        else:
                            if verbose:
                                console.print(
                                    f"  [yellow]⊘[/yellow] No vulnerabilities found in {report_file.name}",
                                    style="dim",
                                )
                    except subprocess.CalledProcessError as e:
                        console.print(
                            f"[red]Error[/red] scanning SBOM {report_file.name}: {e.stderr}",
                            style="bold red",
                        )
                    except json.JSONDecodeError as e:
                        console.print(
                            f"[red]Error[/red] parsing Grype output for {report_file.name}: {e}",
                            style="bold red",
                        )
                else:
                    if verbose:
                        console.print(
                            f"[yellow]⊘[/yellow] Skipped (unknown format): {report_file.name}",
                            style="dim",
                        )
        except json.JSONDecodeError as e:
            console.print(f"[red]Error[/red] loading {report_file.name}: {e}", style="bold red")
        except Exception as e:
            console.print(
                f"[red]Unexpected error[/red] loading {report_file.name}: {e}",
                style="bold red",
            )

    return reports
