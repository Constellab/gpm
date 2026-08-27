# syntax=docker/dockerfile:1.6

# =============================================================================
# Build Arguments
# =============================================================================
ARG IMAGE="constellab/glab:latest"

FROM $IMAGE

LABEL maintainer="Admin <admin@gencovery.com>"

# =============================================================================
# Build Arguments (re-declare after FROM)
# =============================================================================
# OpenVSCode Server configuration
# Choose version from https://github.com/gitpod-io/openvscode-server
ARG RELEASE_TAG=openvscode-server-v1.109.5
ARG RELEASE_ORG="gitpod-io"
ARG OPENVSCODE_SERVER_ROOT="/opt/openvscode-server"

# =============================================================================
# Environment Variables
# =============================================================================
ENV TZ=UTC \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    EDITOR=code \
    VISUAL=code \
    GIT_EDITOR="code --wait" \
    OPENVSCODE_SERVER_ROOT=${OPENVSCODE_SERVER_ROOT} \
    INIT_LAB_PATH=/init-lab

# =============================================================================
# System Package Installation
# =============================================================================
USER root
WORKDIR /home

# Install system dependencies:
# - git: Version control, required for OpenVSCode Server extensions
# - wget: Download OpenVSCode Server release
# openssh-server and rsyslog come from the glab base image (SSH is opt-in there,
# see ENABLE_SSH_SERVER below).
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    rm -f /etc/apt/apt.conf.d/docker-clean && \
    sed -i 's|http://archive.ubuntu.com|http://azure.archive.ubuntu.com|g; s|http://security.ubuntu.com|http://azure.archive.ubuntu.com|g' \
        /etc/apt/sources.list /etc/apt/sources.list.d/ubuntu.sources 2>/dev/null || true; \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        wget && \
    rm -rf /tmp/* /var/tmp/*

# =============================================================================
# Python Dependencies Installation
# =============================================================================
# Install ruff (Python linter/formatter) and pyright (Python type checker) into the glab venv (/home/labuser/.venv).
# Must run as labuser because root can't write to the labuser-owned venv.
USER labuser
RUN uv pip install --no-cache ruff pyright
USER root

# =============================================================================
# OpenVSCode Server Installation
# =============================================================================
# Download and install OpenVSCode Server
# Based on https://github.com/gitpod-io/openvscode-releases/blob/main/Dockerfile
# Note: SHA256 checksums are not published with releases
RUN if [ -z "${RELEASE_TAG}" ]; then \
        echo "The RELEASE_TAG build arg must be set." >&2 && \
        exit 1; \
    fi && \
    # Detect architecture and map to OpenVSCode naming convention
    arch=$(uname -m) && \
    if [ "${arch}" = "x86_64" ]; then \
        arch="x64"; \
    elif [ "${arch}" = "aarch64" ]; then \
        arch="arm64"; \
    elif [ "${arch}" = "armv7l" ]; then \
        arch="armhf"; \
    fi && \
    ARCHIVE="${RELEASE_TAG}-linux-${arch}.tar.gz" && \
    DOWNLOAD_URL="https://github.com/${RELEASE_ORG}/openvscode-server/releases/download/${RELEASE_TAG}" && \
    # Download release archive
    wget "${DOWNLOAD_URL}/${ARCHIVE}" && \
    # Extract and install
    tar -xzf "${ARCHIVE}" && \
    mv -f "${RELEASE_TAG}-linux-${arch}" "${OPENVSCODE_SERVER_ROOT}" && \
    # Create 'code' alias for convenience (matches VS Code CLI)
    cp "${OPENVSCODE_SERVER_ROOT}/bin/remote-cli/openvscode-server" \
       "${OPENVSCODE_SERVER_ROOT}/bin/remote-cli/code" && \
    # Cleanup
    rm -f "${ARCHIVE}"

# =============================================================================
# VS Code Remote Setup
# =============================================================================
RUN mkdir -p /home/labuser/.vscode-server \
        /home/labuser/.openvscode-server && \
    # Set ownership for VS Code server directories (so they can be used in volume)
    chown labuser:labuser /home/labuser/.vscode-server && \
    chown labuser:labuser /home/labuser/.openvscode-server

# =============================================================================
# SSH Server
# =============================================================================
# The SSH server itself (package, sshd_config, init-ssh.sh) lives in the glab
# base image, where it is disabled by default. Codelab enables it by default
# because VS Code Remote SSH is one of its features. Set ENABLE_SSH_SERVER to
# false at runtime to start codelab without any sshd process listening.
ENV ENABLE_SSH_SERVER=true

# =============================================================================
# Application Setup
# =============================================================================
# Copy initialization scripts from base image location
# NOTE: The glab base image already includes these files at /init-lab
# This copy ensures codelab has its own layer for cache control and flexibility
COPY --chown=labuser:labuser ./init ${INIT_LAB_PATH}

# Make entrypoint script executable
RUN chmod +x /init-lab/entrypoint-codelab.sh

# =============================================================================
# Runtime Configuration
# =============================================================================
# Default to labuser so `docker exec` lands as labuser with a proper env.
# Sub-composes that need to run the entrypoint as root (for UID/GID alignment
# on bind-mounts) must override this with `user: "0:0"` — the normal case
# uses `user: "${HOST_UID}:${HOST_GID}"` which already sets a non-root user.
USER labuser
WORKDIR /lab/user/

ENTRYPOINT [ "/init-lab/entrypoint-codelab.sh" ]
