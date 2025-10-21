"""Scanner integration for Grype and Trivy vulnerability scanners."""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from rich.console import Console

from ..core.constants import FIELD_ARTIFACTS, FIELD_DESCRIPTOR, FIELD_MATCHES, FIELD_SCANNER, FIELD_SOURCE_FILE
from ..core.exceptions import ReportLoadError, ScannerExecutionError, ScannerNotFoundError
from ..core.models import ScannerType

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
        error_msg = f"Converting {grype_report.name} to CycloneDX: {e.stderr}"
        console.print(f"[red]Error[/red] {error_msg}", style="bold red")
        raise ScannerExecutionError(
            "syft", ["syft", "convert", str(grype_report), "-o", "cyclonedx-json"], e.stderr
        ) from e
    except FileNotFoundError as e:
        console.print(
            "[red]Error:[/red] 'syft' command not found. Please install syft to use Trivy scanning.",
            style="bold red",
        )
        raise ScannerNotFoundError("syft") from e


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
        error_msg = f"Scanning {cdx_file.name} with Trivy"
        console.print(f"[red]Error[/red] {error_msg}: {e}", style="bold red")
        raise ScannerExecutionError(
            "trivy", ["trivy", "sbom", str(cdx_file), "-f", "json", "-o", str(trivy_report)], str(e)
        ) from e
    except FileNotFoundError as e:
        console.print(
            "[red]Error:[/red] 'trivy' command not found. Please install Trivy.",
            style="bold red",
        )
        raise ScannerNotFoundError("trivy") from e


def process_trivy_reports(reports_dir: Path, verbose: bool = False) -> list[dict[str, Any]]:
    """Process reports for Trivy scanning.

    Handles two scenarios:
    1. SBOM files: Scans directly with Trivy
    2. Grype reports: Converts to CycloneDX first, then scans with Trivy

    Args:
        reports_dir: Directory containing JSON reports or SBOM files.
        verbose: Whether to print detailed processing information.

    Returns:
        List of Trivy report dictionaries.
    """
    # Create temporary directory for intermediate files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path: Path = Path(temp_dir)
        trivy_reports: list[dict[str, Any]] = []

        # Search recursively for JSON files (handles subdirectories from downloaded packages)
        json_files: list[Path] = list(reports_dir.rglob("*.json"))
        if not json_files:
            error_msg = f"No JSON files found in '{reports_dir}'"
            console.print(f"[red]Error:[/red] {error_msg}", style="bold red")
            raise ReportLoadError(str(reports_dir), "No JSON files found in directory")

        report_file: Path
        for report_file in json_files:
            try:
                # Read the file to determine its type
                with open(report_file) as f:
                    data: dict[str, Any] = json.load(f)

                # Check if this is a Syft SBOM (has "artifacts" and "descriptor" fields)
                is_sbom = data.get(FIELD_ARTIFACTS) and data.get(FIELD_DESCRIPTOR)

                if is_sbom:
                    # This is a Syft SBOM, scan directly with Trivy
                    if verbose:
                        console.print(
                            f"[cyan]Scanning SBOM[/cyan] {report_file.name} with Trivy...",
                            style="dim",
                        )

                    # Scan the SBOM with Trivy
                    trivy_report_path = scan_with_trivy(report_file, temp_path, verbose)

                    # Load the Trivy report
                    with open(trivy_report_path) as f:
                        trivy_data: dict[str, Any] = json.load(f)
                        # Store relative path for package grouping
                        trivy_data[FIELD_SOURCE_FILE] = str(report_file.relative_to(reports_dir))
                        trivy_data[FIELD_SCANNER] = "trivy"
                        trivy_reports.append(trivy_data)

                    if verbose:
                        console.print(
                            f"  [green]✓[/green] Scanned: {report_file.name}",
                            style="dim",
                        )

                elif data.get(FIELD_MATCHES):
                    # This is a Grype report, convert to CycloneDX then scan
                    if verbose:
                        console.print(
                            f"[cyan]Converting and scanning[/cyan] {report_file.name} with Trivy...",
                            style="dim",
                        )

                    # Convert to CycloneDX
                    cdx_file = convert_to_cyclonedx(report_file, temp_path, verbose)

                    # Scan with Trivy
                    trivy_report_path = scan_with_trivy(cdx_file, temp_path, verbose)

                    # Load the Trivy report
                    with open(trivy_report_path) as f:
                        trivy_data = json.load(f)
                        # Store relative path for package grouping
                        trivy_data[FIELD_SOURCE_FILE] = str(report_file.relative_to(reports_dir))
                        trivy_data[FIELD_SCANNER] = "trivy"
                        trivy_reports.append(trivy_data)

                    if verbose:
                        console.print(
                            f"  [green]✓[/green] Scanned: {report_file.name}",
                            style="dim",
                        )

                else:
                    # Unknown format, skip
                    if verbose:
                        console.print(
                            f"[yellow]⊘[/yellow] Skipped (unknown format): {report_file.name}",
                            style="dim",
                        )

            except json.JSONDecodeError as e:
                console.print(
                    f"[red]Error[/red] parsing JSON in {report_file.name}: {e}",
                    style="bold red",
                )
                continue
            except Exception as e:
                console.print(
                    f"[red]Error[/red] processing {report_file.name}: {e}",
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
    # Use rglob to search recursively for JSON files in subdirectories
    json_files: list[Path] = list(reports_dir.rglob("*.json"))
    if not json_files:
        error_msg = f"No JSON files found in '{reports_dir}'"
        console.print(f"[red]Error:[/red] {error_msg}", style="bold red")
        raise ReportLoadError(str(reports_dir), "No JSON files found in directory")

    report_file: Path
    for report_file in json_files:
        try:
            with open(report_file) as f:
                data: dict[str, Any] = json.load(f)

                # Check if this is a Grype scan result (has "matches" field)
                if data.get(FIELD_MATCHES):
                    # Store relative path to reports_dir for package grouping
                    data[FIELD_SOURCE_FILE] = str(report_file.relative_to(reports_dir))
                    data[FIELD_SCANNER] = "grype"
                    reports.append(data)
                    if verbose:
                        match_count: int = len(data.get("matches", []))
                        console.print(
                            f"[green]✓[/green] Loaded: {report_file.name} ([cyan]{match_count}[/cyan] matches)",
                            style="dim",
                        )
                # Check if this is a Syft SBOM (has "artifacts" and "descriptor" fields)
                elif data.get(FIELD_ARTIFACTS) and data.get(FIELD_DESCRIPTOR):
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

                        if scan_data.get(FIELD_MATCHES):
                            # Store relative path to reports_dir for package grouping
                            scan_data[FIELD_SOURCE_FILE] = str(report_file.relative_to(reports_dir))
                            scan_data[FIELD_SCANNER] = "grype"
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
