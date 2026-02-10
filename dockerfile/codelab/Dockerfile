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
ARG RELEASE_TAG=openvscode-server-v1.105.1
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
# - openssh-server: Enable SSH access for VS Code Remote
# - rsyslog: Logging for SSH authentication and debugging
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        wget \
        openssh-server \
        rsyslog && \
    # Clean apt cache to reduce image size
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# =============================================================================
# Python Dependencies Installation
# =============================================================================
# Install ruff (Python linter/formatter) system-wide
# Version pinned to 0.14.7 for consistency
RUN pip install --no-cache-dir ruff==0.14.7

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
# SSH Server Configuration and VS Code Remote Setup
# =============================================================================
# Configure SSH server for VS Code Remote access
RUN mkdir -p /etc/ssh /home/labuser/.ssh \
        /home/labuser/.vscode-server \
        /home/labuser/.openvscode-server && \
    # Set proper ownership and permissions for SSH directory (mode 700 required)
    chown labuser:labuser /home/labuser/.ssh && \
    chmod 700 /home/labuser/.ssh && \
    # Set ownership for VS Code server directories (so they can be used in volume)
    chown labuser:labuser /home/labuser/.vscode-server && \
    chown labuser:labuser /home/labuser/.openvscode-server && \
    # Create locale file to avoid PAM environment warnings
    touch /etc/default/locale && \
    echo "LANG=C.UTF-8" > /etc/default/locale

# Copy SSH and rsyslog configuration files
# sshd_config: Restricts to labuser, pubkey auth only, enables port forwarding
# rsyslog.conf: Disables kernel logging (unavailable in containers)
COPY ./dockerfile/codelab/sshd_config /tmp/sshd_config
COPY ./dockerfile/codelab/rsyslog.conf /etc/rsyslog.conf

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
# Switch back to labuser for runtime security
USER labuser
WORKDIR /lab/user/

ENTRYPOINT [ "/init-lab/entrypoint-codelab.sh" ]
