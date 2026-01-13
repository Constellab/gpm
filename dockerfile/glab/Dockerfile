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
    CUSTOM_PIP_VERSION=25.3 \
    CUSTOM_MAMBA_VERSION=25.9.1-0 \
    PATH="/home/labuser/.local/bin:/opt/conda/bin:${PATH}"

# ============================================================================
# System Package Installation
# ============================================================================

# Install Python 3.10 and essential system packages
RUN apt-get -y update && \
    apt-get -y install python3.10 python3-distutils && \
    apt-get -y install git curl zip unzip bzip2 wget rsync nginx sudo && \
    # It is needed to install hdmedians which is a dependency of scikit-bio
    # build essential install g++ and gcc which are commonly needed
    apt-get -y install gcc libpq-dev python3-dev build-essential && \
    # create a symlink to python3 so python command will use python3
    ln -s $(which python3) /usr/local/bin/python && \
    # Clean apt cache to reduce image size
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# ============================================================================
# Python Package Managers Installation
# ============================================================================

# Install pip system-wide (as root) so it's available to all users
# Using -fsSL for secure download: fail on errors, silent, follow redirects, HTTPS
RUN curl -fsSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3 get-pip.py "pip==${CUSTOM_PIP_VERSION}" && \
    python3 -m pip install --no-cache-dir --upgrade setuptools && \
    rm get-pip.py

# Installing conda and mamba system-wide (as root)
# Info from https://github.com/conda-forge/miniforge#mambaforge
# Download installer and its SHA256 checksum, then verify before installation
RUN INSTALLER="Miniforge3-${CUSTOM_MAMBA_VERSION}-$(uname)-$(uname -m).sh" && \
    RELEASE_URL="https://github.com/conda-forge/miniforge/releases/download/${CUSTOM_MAMBA_VERSION}" && \
    curl -fsSL "${RELEASE_URL}/${INSTALLER}" -o "${INSTALLER}" && \
    curl -fsSL "${RELEASE_URL}/${INSTALLER}.sha256" -o "${INSTALLER}.sha256" && \
    sha256sum -c "${INSTALLER}.sha256" && \
    bash "${INSTALLER}" -b -p /opt/conda && \
    rm "${INSTALLER}" "${INSTALLER}.sha256" && \
    /opt/conda/bin/conda init bash && \
    /opt/conda/bin/mamba shell init --shell bash

# ============================================================================
# Python Dependencies Installation
# ============================================================================

# Install pipenv and gws dependencies system-wide (as root)
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

USER labuser
WORKDIR /home/labuser

# ============================================================================
# Application Setup
# ============================================================================

COPY --chown=labuser:labuser ./init /init-lab

# Make entrypoint script executable
RUN chmod +x /init-lab/entrypoint-glab.sh

ENTRYPOINT [ "/init-lab/entrypoint-glab.sh" ]
