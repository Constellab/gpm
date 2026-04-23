# syntax=docker/dockerfile:1.6

# Build arguments - define before FROM for better visibility
ARG IMAGE="ubuntu:22.04"

FROM $IMAGE

# Re-declare build arguments after FROM (ARGs before FROM are not available after)
ARG USER_ID=1000
ARG GROUP_ID=1000

LABEL maintainer="Admin <admin@gencovery.com>"

# ============================================================================
# Environment Variables
# ============================================================================
ENV TZ=UTC \
    # Version from https://github.com/conda-forge/miniforge/releases
    CUSTOM_MAMBA_VERSION=25.11.0-1 \
    # don't name it PIP_VERSION because it will be overwritten by pip
    # version from https://pypi.org/project/pip/
    CUSTOM_PIP_VERSION=26.0 \
    # User local bin first, then system paths, then conda at the end
    # so system Python 3.10 takes precedence over conda's Python
    PATH="/home/labuser/.local/bin:$PATH:/opt/conda/bin"

# ============================================================================
# System Package Installation
# ============================================================================

# install python v 3.10 & base packages
# Use the Azure Ubuntu mirror — GitHub runners are on Azure, so this is much
# faster than the default archive.ubuntu.com.
# BuildKit cache mounts persist /var/cache/apt and /var/lib/apt/lists across
# builds, so apt downloads are reused even when the layer hash changes.
# The base image's docker-clean config auto-deletes downloaded debs, which
# defeats the cache mount — remove it first.
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    rm -f /etc/apt/apt.conf.d/docker-clean && \
    sed -i 's|http://archive.ubuntu.com|http://azure.archive.ubuntu.com|g; s|http://security.ubuntu.com|http://azure.archive.ubuntu.com|g' /etc/apt/sources.list && \
    apt-get -y update && \
    apt-get -y install \
        python3.10 python3-distutils \
        git curl zip unzip bzip2 wget rsync nginx sudo pigz \
        gcc libpq-dev python3-dev build-essential && \
    ln -s $(which python3) /usr/local/bin/python

# install pip system-wide (as root) so it's available to all users
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3 get-pip.py "pip==${CUSTOM_PIP_VERSION}" && \
    python3 -m pip install --upgrade setuptools && \
    rm get-pip.py

# ============================================================================
# Conda/Mamba Installation (includes Python 3.10 and pip)
# ============================================================================

# Install miniforge (conda + mamba) with Python 3.10
# Info from https://github.com/conda-forge/miniforge#mambaforge
# Download installer and its SHA256 checksum, then verify before installation
# Installing conda and mamba system-wide (as root)
# Info from https://github.com/conda-forge/miniforge#mambaforge
RUN curl -L https://github.com/conda-forge/miniforge/releases/download/${CUSTOM_MAMBA_VERSION}/Miniforge3-${CUSTOM_MAMBA_VERSION}-$(uname)-$(uname -m).sh -o mamba_install.sh && \
    bash mamba_install.sh -b -p /opt/conda && \
    rm mamba_install.sh && \
    /opt/conda/bin/conda init bash && \
    /opt/conda/bin/mamba shell init --shell bash && \
    # Clean conda cache to reduce image size
    /opt/conda/bin/conda clean -afy

# ============================================================================
# Python Dependencies Installation
# ============================================================================

# Install initial dependencies using conda's pip
RUN pip install --no-cache-dir \
                pipenv==2025.0.4 \
                click==8.3.1 \
                GitPython==3.1.45 \
                requests==2.32.5

# ============================================================================
# User Setup
# ============================================================================

# Create non-root user matching host ubuntu user
# Configure sudo access via sudoers.d for convenience (security trade-off)
RUN groupadd -g ${GROUP_ID} labuser && \
    useradd -m -u ${USER_ID} -g ${GROUP_ID} -s /bin/bash labuser && \
    echo "labuser ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/labuser && \
    chmod 0440 /etc/sudoers.d/labuser

# Default to labuser so `docker exec` lands as labuser with a proper env.
# Sub-composes that need to run the entrypoint as root (for UID/GID alignment
# on bind-mounts) must override this with `user: "0:0"` — the normal case
# uses `user: "${HOST_UID}:${HOST_GID}"` which already sets a non-root user.
USER labuser
WORKDIR /home/labuser

# ============================================================================
# Application Setup
# ============================================================================

COPY --chown=labuser:labuser ./init /init-lab

# Make entrypoint script executable
RUN chmod +x /init-lab/entrypoint-glab.sh

ENTRYPOINT [ "/init-lab/entrypoint-glab.sh" ]
