"""Package downloader for fetching SBOM reports from remote registries."""

from pathlib import Path

from rich.console import Console

from ..core.config import get_current_config
from ..core.executor import ExecutorManager
from ..core.logging import get_logger
from ..core.models import PackageConfig

console = Console()
logger = get_logger(__name__)


def download_package_sboms(output_dir: Path) -> list[Path]:
    """Download SBOM reports for all configured packages.

    This function uses the `uds zarf package inspect sbom` command to download
    SBOM reports from a remote registry for each package specified in the
    configuration. The command extracts SBOM files to a directory, and this
    function locates and copies the SBOM JSON files to the output directory.

    Args:
        output_dir: Directory to store downloaded SBOM reports

    Returns:
        List of paths to downloaded SBOM JSON files

    Raises:
        ValueError: If required configuration is missing
        RuntimeError: If download fails for any package
    """
    config = get_current_config()

    # Validate required configuration
    if not config.downloadRemotePackages:
        logger.debug("downloadRemotePackages is False, skipping package downloads")
        return []

    if not config.registry:
        raise ValueError("Registry URL is required when downloadRemotePackages is enabled")

    if not config.organization:
        raise ValueError("Organization is required when downloadRemotePackages is enabled")

    if not config.packages:
        logger.warning("No packages configured for download")
        return []

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    downloaded_files: list[Path] = []

    if config.verbose:
        console.print(f"\n[cyan]Downloading SBOM reports for {len(config.packages)} packages...[/cyan]")

    for package in config.packages:
        try:
            sbom_files = download_package_sbom(
                package=package,
                registry=config.registry,
                organization=config.organization,
                output_dir=output_dir,
                verbose=config.verbose,
            )
            downloaded_files.extend(sbom_files)

            if config.verbose:
                for sbom_file in sbom_files:
                    console.print(f"  [green]✓[/green] Downloaded: {sbom_file.name}")

        except Exception as e:
            error_msg = f"Failed to download SBOM for {package.name}-{package.version}: {e}"
            logger.error("Package download failed", package=package.name, error=str(e))

            if config.verbose:
                console.print(f"  [red]✗[/red] {error_msg}")

            # Continue with other packages instead of failing completely
            continue

    if config.verbose:
        console.print(
            f"\n[green]✓[/green] Downloaded {len(downloaded_files)} SBOM files from {len(config.packages)} packages\n"
        )

    return downloaded_files


def download_package_sbom(
    package: PackageConfig,
    registry: str,
    organization: str,
    output_dir: Path,
    verbose: bool = False,
) -> list[Path]:
    """Download SBOM report for a single package from remote registry.

    Uses the `uds zarf package inspect sbom` command to download the SBOM
    report for a specific package. The command extracts SBOM files to a
    temporary directory created via `mktemp -d`, which are then located
    and copied to the output directory.

    Command format:
        uds zarf package inspect sbom <registry>/<organization>/<package-name>-<version> \\
            -a <architecture> --output <temp-dir>

    Args:
        package: Package configuration (name, version, architecture)
        registry: Container registry URL
        organization: Organization or namespace in the registry
        output_dir: Directory to store the downloaded SBOM files
        verbose: Enable verbose output

    Returns:
        List of paths to downloaded SBOM JSON files

    Raises:
        RuntimeError: If the download command fails or temp directory creation fails
        ValueError: If package configuration is invalid
    """
    import shutil

    # Validate package configuration
    if not package.name:
        raise ValueError("Package name is required")
    if not package.version:
        raise ValueError("Package version is required")
    if not package.architecture:
        raise ValueError("Package architecture is required")

    # Construct package reference
    # Format: <registry>/<organization>/<package-name>-<version>
    package_ref = f"{registry}/{organization}/{package.name}-{package.version}"

    # Create a temporary directory using ExecutorManager
    temp_dir, temp_error = ExecutorManager.create_temp_directory(config=get_current_config())

    if temp_error:
        raise RuntimeError(f"Failed to create temporary directory: {temp_error}")

    try:
        package_temp_dir = temp_dir / f"{package.name}-sbom"

        # Build the command
        # uds zarf package inspect sbom <package-ref> -a <arch> --output <dir>
        command = [
            "uds",
            "zarf",
            "package",
            "inspect",
            "sbom",
            package_ref,
            "-a",
            package.architecture,
            "--output",
            str(package_temp_dir),
        ]

        if verbose:
            logger.info(
                "Downloading package SBOM",
                package=package.name,
                version=package.version,
                architecture=package.architecture,
                registry=registry,
                organization=organization,
            )

        # Execute the command
        _, error = ExecutorManager.execute(command, cwd=None, config=get_current_config())

        if error:
            error_msg = f"Failed to download SBOM for {package.name}-{package.version}"
            logger.error(
                "SBOM download failed",
                package=package.name,
                version=package.version,
                error=str(error),
            )
            raise RuntimeError(error_msg) from error

        # Find all JSON files in the downloaded directory
        sbom_files: list[Path] = []
        if package_temp_dir.exists():
            # Search for JSON files recursively
            json_files = list(package_temp_dir.rglob("*.json"))

            for json_file in json_files:
                # Create a unique name for the file in the output directory
                # Format: <package-name>-<version>-<original-filename>
                output_filename = f"{package.name}-{package.version}-{json_file.name}"
                output_path = output_dir / output_filename

                # Copy the file to the output directory
                shutil.copy2(json_file, output_path)
                sbom_files.append(output_path)

                if verbose:
                    logger.debug(
                        "Copied SBOM file",
                        source=str(json_file),
                        destination=str(output_path),
                    )

        if not sbom_files:
            logger.warning(
                "No SBOM JSON files found for package",
                package=package.name,
                version=package.version,
            )

        return sbom_files

    finally:
        # Clean up temporary directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            if verbose:
                logger.debug("Cleaned up temporary directory", temp_dir=str(temp_dir))
