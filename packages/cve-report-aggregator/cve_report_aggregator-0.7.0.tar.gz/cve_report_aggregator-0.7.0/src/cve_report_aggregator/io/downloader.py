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
    if not config.download_remote_packages:
        logger.debug("download_remote_packages is False, skipping package downloads")
        return []

    if not config.registry:
        raise ValueError("Registry URL is required when download_remote_packages is enabled")

    if not config.organization:
        raise ValueError("Organization is required when download_remote_packages is enabled")

    if not config.packages:
        logger.warning("No packages configured for download")
        return []

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    downloaded_files: list[Path] = []

    is_debug = config.log_level == "DEBUG"
    if is_debug:
        console.print(f"\n[cyan]Downloading SBOM reports for {len(config.packages)} packages...[/cyan]")

    for package in config.packages:
        try:
            sbom_files = download_package_sbom(
                package=package,
                registry=config.registry,
                organization=config.organization,
                output_dir=output_dir,
            )
            downloaded_files.extend(sbom_files)

            if is_debug:
                for sbom_file in sbom_files:
                    console.print(f"  [green]✓[/green] Downloaded: {sbom_file.name}")

        except Exception as e:
            error_msg = f"Failed to download SBOM for {package.name}-{package.version}: {e}"
            logger.error("Package download failed", package=package.name, error=str(e))

            if is_debug:
                console.print(f"  [red]✗[/red] {error_msg}")

            # Continue with other packages instead of failing completely
            continue

    if is_debug:
        console.print(
            f"\n[green]✓[/green] Downloaded {len(downloaded_files)} SBOM files from {len(config.packages)} packages\n"
        )

    return downloaded_files


def download_package_sbom(
    package: PackageConfig, registry: str, organization: str, output_dir: Path, protocol: str = "oci"
) -> list[Path]:
    """Download SBOM report for a single package from remote registry.

    Uses the `uds zarf package inspect sbom` command to download the SBOM
    report for a specific package. The command extracts SBOM files directly
    to the output directory under a package-specific subdirectory.

    Command format:
        uds zarf package inspect sbom <registry>/<organization>/<package-name>-<version> \\
            -a <architecture> --output <output-dir>/<package-name>

    Args:
        package: Package configuration (name, version, architecture)
        registry: Container registry URL
        organization: Organization or namespace in the registry
        output_dir: Directory to store the downloaded SBOM files

    Returns:
        List of paths to downloaded SBOM JSON files

    Raises:
        RuntimeError: If the download command fails
        ValueError: If package configuration is invalid
    """
    # Validate package configuration
    if not package.name:
        raise ValueError("Package name is required")
    if not package.version:
        raise ValueError("Package version is required")
    if not package.architecture:
        raise ValueError("Package architecture is required")

    # Get current config for log level check
    config = get_current_config()
    is_debug = config.log_level == "DEBUG"

    # Map application log level to UDS CLI log level
    # Application: DEBUG, INFO, WARNING, ERROR, CRITICAL
    # UDS CLI: trace, debug, info, warn
    uds_log_level_map = {
        "DEBUG": "debug",
        "INFO": "info",
        "WARNING": "warn",
        "ERROR": "warn",
        "CRITICAL": "trace",
    }
    uds_log_level = uds_log_level_map.get(config.log_level, "info")

    # Construct package reference
    # Format: <registry>/<organization>/<package-name>:<version>
    package_ref = f"{registry}/{organization}/{package.name}:{package.version}"

    # Build the command
    # uds zarf package inspect sbom <package-ref> -a <arch> --output <dir> --log-level <level>
    # Note: The uds command automatically creates a subdirectory named after the package
    # So passing --output reports will create reports/<package-name>/
    command = [
        "uds",
        "zarf",
        "package",
        "inspect",
        "sbom",
        f"{protocol}://{package_ref}",
        "-a",
        package.architecture,
        "--output",
        str(output_dir),
        "--log-level",
        uds_log_level,
    ]

    # The uds command will create this directory
    package_output_dir = output_dir / package.name

    if is_debug:
        logger.info(
            "Downloading package SBOM",
            package=package.name,
            version=package.version,
            architecture=package.architecture,
            registry=registry,
            organization=organization,
            output_dir=str(package_output_dir),
        )

    # Execute the command
    _, error = ExecutorManager.execute(command, cwd=None, config=config)

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
    if package_output_dir.exists():
        # Search for JSON files recursively
        json_files = list(package_output_dir.rglob("*.json"))

        for json_file in json_files:
            sbom_files.append(json_file)

            if is_debug:
                logger.debug(
                    "Found SBOM file",
                    package=package.name,
                    file=str(json_file.relative_to(output_dir)),
                )

    if not sbom_files:
        logger.warning(
            "No SBOM JSON files found for package",
            package=package.name,
            version=package.version,
        )

    return sbom_files
