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
    # All Python work happens inside a labuser-owned venv at /home/labuser/.venv.
    # Putting its bin dir first on PATH and exporting VIRTUAL_ENV auto-activates
    # the venv for every shell (interactive or not) — `python3`, `pip`, and any
    # bare `uv pip install` invocation resolve to and install into this venv.
    # User-local bin stays second for any user-scoped tooling; conda trails.
    VIRTUAL_ENV=/home/labuser/.venv \
    PATH="/home/labuser/.venv/bin:/home/labuser/.local/bin:$PATH:/opt/conda/bin" \
    # pipenv is used for per-project isolated environments. Without this, pipenv
    # would detect VIRTUAL_ENV and install project deps into the glab venv
    # instead of creating a project-specific one.
    PIPENV_IGNORE_VIRTUALENVS=1

# ============================================================================
# System Package Installation
# ============================================================================

# install python v 3.10 & base packages
# openssh-server + rsyslog are installed but never started unless
# ENABLE_SSH_SERVER is enabled at runtime — see the "SSH Server" section below.
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
        gcc libpq-dev python3-dev build-essential \
        openssh-server rsyslog && \
    ln -s $(which python3) /usr/local/bin/python

# install pip system-wide (as root) so it's available to all users
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3 get-pip.py "pip==${CUSTOM_PIP_VERSION}" && \
    python3 -m pip install --upgrade setuptools && \
    rm get-pip.py

# Install uv (fast Python package installer) system-wide so it's on PATH
# for both root and labuser. Pinned version from https://github.com/astral-sh/uv/releases
ENV UV_VERSION=0.5.11
RUN curl -LsSf https://astral.sh/uv/${UV_VERSION}/install.sh | \
    env UV_INSTALL_DIR=/usr/local/bin INSTALLER_NO_MODIFY_PATH=1 sh && \
    uv --version

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
# User Setup
# ============================================================================

# Create non-root user matching host ubuntu user
# Configure sudo access via sudoers.d for convenience (security trade-off)
RUN groupadd -g ${GROUP_ID} labuser && \
    useradd -m -u ${USER_ID} -g ${GROUP_ID} -s /bin/bash labuser && \
    echo "labuser ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/labuser && \
    chmod 0440 /etc/sudoers.d/labuser

# ============================================================================
# SSH Server (opt-in, disabled by default)
# ============================================================================

# The SSH server ships in the image so that any lab can offer SSH access, but
# it is OFF unless ENABLE_SSH_SERVER is truthy (true/1/yes/on) at runtime.
# Nothing in the image starts sshd on its own — the container has no init
# system, and /init-lab/init-ssh.sh is the only thing that launches it. With
# the flag off there is no host key, no sshd/rsyslog process and no open port,
# so the container exposes no SSH attack surface.
ENV ENABLE_SSH_SERVER=false

# sshd_config: port 2222, labuser only, pubkey auth only, TCP forwarding on
#              (required by VS Code Remote SSH).
# rsyslog.conf: disables kernel logging, which is unavailable in containers.
# sshd_config is staged under /opt because /etc/ssh may be a mounted volume;
# init-ssh.sh copies it into place at startup. Not /tmp: downstream images
# (codelab) clear /tmp in their own layers.
COPY ./dockerfile/glab/sshd_config /opt/glab/sshd_config
COPY ./dockerfile/glab/rsyslog.conf /etc/rsyslog.conf

RUN mkdir -p /etc/ssh /home/labuser/.ssh && \
    # Set proper ownership and permissions for SSH directory (mode 700 required)
    chown labuser:labuser /home/labuser/.ssh && \
    chmod 700 /home/labuser/.ssh && \
    # Drop the host keys generated by the openssh-server package: baking them
    # into the image would give every container the same SSH identity.
    # init-ssh.sh regenerates them per container, only when SSH is enabled.
    rm -f /etc/ssh/ssh_host_* && \
    # Create locale file to avoid PAM environment warnings
    echo "LANG=C.UTF-8" > /etc/default/locale

# Default to labuser so `docker exec` lands as labuser with a proper env.
# Sub-composes that need to run the entrypoint as root (for UID/GID alignment
# on bind-mounts) must override this with `user: "0:0"` — the normal case
# uses `user: "${HOST_UID}:${HOST_GID}"` which already sets a non-root user.
USER labuser
WORKDIR /home/labuser

# ============================================================================
# Python Dependencies Installation
# ============================================================================

# Create the labuser-owned venv that VIRTUAL_ENV/PATH point at, using the
# system Python 3.10. --system-site-packages lets code in the venv still
# import packages installed system-wide (e.g. pipenv, click copies pip pulls in)
# when needed. `uv venv` is used instead of `python3 -m venv` because the base
# image doesn't include python3-venv (the stdlib ensurepip module).
# align-user.sh's `chown -R /home/labuser` at UID-remap time covers the venv,
# so it stays writable across host-UID changes.
RUN uv venv --system-site-packages --python python3 "${VIRTUAL_ENV}"

# Install initial dependencies into the venv. uv auto-detects VIRTUAL_ENV and
# installs into it without any --system / --user / --prefix flag.
RUN uv pip install --no-cache \
                pipenv==2025.0.4 \
                click==8.3.1 \
                GitPython==3.1.45 \
                requests==2.32.5

# ============================================================================
# Application Setup
# ============================================================================

COPY --chown=labuser:labuser ./init /init-lab

# Make entrypoint script executable
RUN chmod +x /init-lab/entrypoint-glab.sh

ENTRYPOINT [ "/init-lab/entrypoint-glab.sh" ]
