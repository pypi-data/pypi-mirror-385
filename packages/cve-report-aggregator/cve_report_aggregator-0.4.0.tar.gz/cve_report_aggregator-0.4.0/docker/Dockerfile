# syntax=docker/dockerfile:1.7

ARG PYTHON_VERSION=3.12.12
ARG GRYPE_VERSION=v0.101.1
ARG SYFT_VERSION=v1.34.2
ARG TRIVY_VERSION=0.67.2
ARG UDS_VERSION=v0.27.15
ARG TARGETARCH=amd64
ARG REGISTRY_URL="registry.defenseunicorns.com"

FROM anchore/grype:${GRYPE_VERSION}-nonroot AS grype
FROM anchore/syft:${SYFT_VERSION}-nonroot AS syft
FROM aquasec/trivy:${TRIVY_VERSION} AS trivy
FROM alpine:3.22.2 AS uds-downloader

ARG UDS_VERSION
ARG TARGETARCH

RUN apk add --no-cache \
        curl=8.14.1-r2 \
        ca-certificates=20250911-r0 \
        jq && \
    set -ex && \
    case "${TARGETARCH}" in \
        amd64) UDS_ARCH="amd64" ;; \
        arm64) UDS_ARCH="arm64" ;; \
        *) echo "Unsupported architecture: ${TARGETARCH}" && exit 1 ;; \
    esac && \
    UDS_URL="https://github.com/defenseunicorns/uds-cli/releases/download/${UDS_VERSION}/uds-cli_${UDS_VERSION}_Linux_${UDS_ARCH}" && \
    echo "Downloading UDS CLI from: ${UDS_URL}" && \
    curl -fsSL --retry 3 --retry-delay 2 "${UDS_URL}" -o /usr/local/bin/uds && \
    if [ ! -s /usr/local/bin/uds ]; then \
        echo "ERROR: Failed to download UDS CLI or file is empty" && \
        echo "Attempted URL: ${UDS_URL}" && \
        exit 1; \
    fi && \
    chmod +x /usr/local/bin/uds && \
    /usr/local/bin/uds version

RUN --mount=type=secret,id=credentials,target=/run/secrets/credentials,required=false \
    if [ -f /run/secrets/credentials ]; then \
        echo "Using credentials from secret mount" && \
        creds=$(cat /run/secrets/credentials) && \
        user=$(echo "$creds" | jq -r .username) && \
        pass=$(echo "$creds" | jq -r .password) && \
        registry=$(echo "$creds" | jq -r .registry) && \
        auth=$(printf '%s' "$user:$pass" | base64 -w0) && \
        jq -n --arg auth "$auth" --arg registry "$registry" '{auths: {($registry): {"auth": $auth}}}' > /root/config.json; \
    else \
        echo "No credentials provided, creating empty Docker config" && \
        echo '{}' > /root/config.json; \
    fi

FROM python:${PYTHON_VERSION}-slim AS python-builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN python -m pip install --no-cache-dir --upgrade pip==25.2 uv==0.5.11

WORKDIR /build

COPY pyproject.toml ./
COPY README.md ./
COPY src/ ./src/
COPY utils/ ./utils/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv venv /opt/venv && \
    uv pip install --python /opt/venv/bin/python .

FROM python:${PYTHON_VERSION}-alpine

WORKDIR /home/cve-aggregator

LABEL maintainer="Mitchell Murphy <mitchell.murphy@defenseunicorns.com>"
LABEL description="CVE Report Aggregator with Grype, Trivy, Syft, and UDS CLI"
LABEL org.opencontainers.image.source="https://github.com/mkm29/cve-report-aggregator"

ARG GRYPE_VERSION
ARG SYFT_VERSION
ARG TRIVY_VERSION
ARG UDS_VERSION
ARG REGISTRY_URL

ENV GRYPE_VERSION=${GRYPE_VERSION} \
    SYFT_VERSION=${SYFT_VERSION} \
    TRIVY_VERSION=${TRIVY_VERSION} \
    UDS_VERSION=${UDS_VERSION}

# Install system dependencies and create non-root user
RUN apk add --no-cache \
        ca-certificates=20250911-r0 \
        curl=8.14.1-r2 \
        git=2.49.1-r0 \
        bash=5.2.37-r0 \
        libgcc=14.2.0-r6 \
        libstdc++=14.2.0-r6 \
        busybox=1.37.0-r19 && \
    addgroup -g 1001 cve-aggregator && \
    adduser -D -u 1001 -G cve-aggregator cve-aggregator

COPY --from=grype /grype /usr/local/bin/grype
COPY --from=syft /syft /usr/local/bin/syft
COPY --from=trivy /usr/local/bin/trivy /usr/local/bin/trivy
COPY --from=uds-downloader /usr/local/bin/uds /usr/local/bin/uds
COPY --from=uds-downloader /root/config.json /tmp/config.json
COPY --from=python-builder /opt/venv /opt/venv

ADD docker/entrypoint.sh /usr/local/bin/entrypoint.sh

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Remove system pip, create workspace, and set permissions
RUN rm -rf /usr/local/lib/python3.12/site-packages/pip* \
           /usr/local/lib/python3.12/ensurepip \
           /usr/local/bin/pip* && \
    mkdir -p /home/cve-aggregator/.docker /home/cve-aggregator/reports /home/cve-aggregator/output && \
    mv /tmp/config.json /home/cve-aggregator/.docker/config.json && \
    chown -R cve-aggregator:cve-aggregator /home/cve-aggregator && \
    chmod -R 755 /home/cve-aggregator && \
    chmod +x /usr/local/bin/entrypoint.sh

USER cve-aggregator

RUN echo "=== Tool Versions ===" && \
    python --version && \
    grype version && \
    syft version && \
    trivy --version && \
    uds version && \
    cve-report-aggregator --version && \
    echo "=== All tools installed successfully ==="

# Set default environment variables (can be overridden at runtime)
ENV REGISTRY_URL=${REGISTRY_URL}
ENV DOCKER_CONFIG="/home/cve-aggregator/.docker"

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
