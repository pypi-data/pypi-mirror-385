# Docker Usage

The Docker container provides a self-contained environment with all required scanning tools pre-installed.

## Quick Start

```bash
# Build the image
docker build -t cve-report-aggregator .

# Run with default settings
docker run --rm cve-report-aggregator --help

# Process reports with mounted volumes
docker run --rm \
  -v $(pwd)/reports:/workspace/reports:ro \
  -v $(pwd)/output:/workspace/output \
  cve-report-aggregator \
  --input-dir /workspace/reports \
  --output-file /workspace/output/unified-report.json \
  --verbose
```

## Docker Credentials Management

The Docker container supports two methods for providing registry credentials:

### Method 1: Build-Time Secrets (Recommended)

**Best for**: Private container images where credentials can be baked in securely.

Create a credentials file in JSON format:

```bash
cat > docker/config.json <<EOF
{
  "username": "myuser",
  "password": "mypassword",
  "registry": "ghcr.io"
}
EOF
chmod 600 docker/config.json
```

!!! warning "Important: Encrypt Before Committing"
    Always encrypt the credentials file with SOPS before committing:

    ```bash
    # Encrypt the credentials file
    sops -e docker/config.json.dec > docker/config.json.enc

    # Or encrypt in place
    sops -e docker/config.json.dec > docker/config.json.enc
    ```

Build the image with the secret:

```bash
# If using encrypted file, decrypt first
sops -d docker/config.json.enc > docker/config.json.dec

# Build with the decrypted credentials
docker buildx build \
  --secret id=credentials,src=./docker/config.json.dec \
  -f docker/Dockerfile \
  -t cve-report-aggregator:latest .

# Remove decrypted file after build
rm docker/config.json.dec
```

Or build directly with unencrypted file (for local development):

```bash
docker buildx build \
  --secret id=credentials,src=./docker/config.json \
  -f docker/Dockerfile \
  -t cve-report-aggregator:latest .
```

The credentials will be stored in the image at `$DOCKER_CONFIG/config.json` (defaults to `/home/cve-aggregator/.docker/config.json`) in proper Docker authentication format with base64-encoded credentials.

Run the container (no runtime credentials needed - uses baked-in config.json):

```bash
docker run --rm cve-report-aggregator:latest --help
```

!!! danger "Security Warning"
    This method bakes credentials into the image. Only use for private registries and **never** push images with credentials to public registries.

### Method 2: Environment Variables (Development Only)

!!! warning "Development Only"
    This method exposes the password in process listings and Docker inspect output. Only use for development/testing.

```bash
docker run -it --rm \
  -e REGISTRY_URL="$UDS_URL" \
  -e UDS_USERNAME="$UDS_USERNAME" \
  -e UDS_PASSWORD="$UDS_PASSWORD" \
  cve-report-aggregator:latest --help
```

## How Credentials Are Handled

The `entrypoint.sh` script checks for Docker authentication on startup:

1. **Docker config.json** (Build-Time): Checks if `$DOCKER_CONFIG/config.json` exists
   - If found: Skips all credential checks and login - uses existing Docker auth
   - Location: `/home/cve-aggregator/.docker/config.json`

2. **Environment Variables** (if config.json not found): Requires all three variables:
   - `REGISTRY_URL` - Registry URL (e.g., `registry.defenseunicorns.com`)
   - `UDS_USERNAME` - Registry username
   - `UDS_PASSWORD` - Registry password

If config.json doesn't exist and environment variables are not provided, the container exits with an error.

## Docker Compose

Use Docker Compose for easier management:

```yaml
version: '3.8'

services:
  cve-aggregator:
    build: .
    volumes:
      - ./reports:/workspace/reports:ro
      - ./output:/workspace/output
    command: >
      --input-dir /workspace/reports
      --output-file /workspace/output/unified-report.json
      --verbose
```

Run with Docker Compose:

```bash
docker compose run cve-aggregator --help
```

## Complete E2E Workflow

Scan container images and aggregate with Docker:

```bash
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v $(pwd)/reports:/workspace/reports \
  -v $(pwd)/output:/workspace/output \
  cve-report-aggregator bash -c "\
    grype nginx:latest -o json > /workspace/reports/nginx.json && \
    grype postgres:15 -o json > /workspace/reports/postgres.json && \
    cve-report-aggregator --input-dir /workspace/reports \
      --output-file /workspace/output/unified.json --verbose"

# View results
jq '.summary' output/unified.json
```

## Next Steps

- [Configuration](../configuration/overview.md) - Configure the aggregator
- [CLI Reference](../user-guide/cli.md) - Full command-line options
