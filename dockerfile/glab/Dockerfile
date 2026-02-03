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
    CUSTOM_MAMBA_VERSION=25.9.1-0 \
    PATH="/home/labuser/.local/bin:/usr/local/bin:/opt/conda/bin:${PATH}"

# ============================================================================
# System Package Installation
# ============================================================================

# Install essential system packages (without Python - conda will provide it)
RUN apt-get -y update && \
    apt-get -y install git curl zip unzip bzip2 wget rsync nginx sudo && \
    # Build tools needed for compiling Python packages (e.g., hdmedians for scikit-bio)
    apt-get -y install gcc libpq-dev build-essential && \
    # Clean apt cache to reduce image size
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# ============================================================================
# Conda/Mamba Installation (includes Python 3.10 and pip)
# ============================================================================

# Install miniforge (conda + mamba) with Python 3.10
# Info from https://github.com/conda-forge/miniforge#mambaforge
# Download installer and its SHA256 checksum, then verify before installation
RUN INSTALLER="Miniforge3-${CUSTOM_MAMBA_VERSION}-$(uname)-$(uname -m).sh" && \
    RELEASE_URL="https://github.com/conda-forge/miniforge/releases/download/${CUSTOM_MAMBA_VERSION}" && \
    curl -fsSL "${RELEASE_URL}/${INSTALLER}" -o "${INSTALLER}" && \
    curl -fsSL "${RELEASE_URL}/${INSTALLER}.sha256" -o "${INSTALLER}.sha256" && \
    sha256sum -c "${INSTALLER}.sha256" && \
    bash "${INSTALLER}" -b -p /opt/conda && \
    rm "${INSTALLER}" "${INSTALLER}.sha256" && \
    # Install Python 3.10 in the base conda environment (includes pip)
    /opt/conda/bin/conda install -y python=3.10 && \
    /opt/conda/bin/conda init bash && \
    /opt/conda/bin/mamba shell init --shell bash && \
    # Clean conda cache to reduce image size
    /opt/conda/bin/conda clean -afy && \
    # Create symlink so 'python' command works
    ln -s /opt/conda/bin/python /usr/local/bin/python

# ============================================================================
# Python Dependencies Installation
# ============================================================================

# Install initial dependencies using conda's pip
RUN /opt/conda/bin/pip install --no-cache-dir \
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
