ARG IMAGE="ubuntu:22.04"
FROM $IMAGE
#FROM "nvidia/cuda:11.2.1-runtime-ubuntu22.04"

LABEL maintainer="Admin <admin@gencovery.com>"

# Set UTC timezone for the docker
ENV TZ=UTC

# don't name it PIP_VERSION because it will be overwritten by pip
# version from https://pypi.org/project/pip/
ENV CUSTOM_PIP_VERSION=25.3
# Version from https://github.com/conda-forge/miniforge/releases
ENV CUSTOM_MAMBA_VERSION=25.9.1

# install python v 3.10 & base packages
RUN apt-get -y update && \
    apt-get -y install python3.10 python3-distutils && \
    apt-get -y install git curl zip unzip bzip2 wget rsync nginx sudo && \
    # It is needed to install hdmedians which is a dependency of scikit-bio
    # build essential install g++ and gcc which are commonly needed
    apt-get -y install gcc libpq-dev python3-dev build-essential && \
    # create a symlink to python3 so python command will use python3
    ln -s $(which python3) /usr/local/bin/python

# install pip system-wide (as root) so it's available to all users
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3 get-pip.py "pip==${CUSTOM_PIP_VERSION}" && \
    python3 -m pip install --upgrade setuptools && \
    rm get-pip.py

# Installing conda and mamba system-wide (as root)
# Info from https://github.com/conda-forge/miniforge#mambaforge
RUN curl -L https://github.com/conda-forge/miniforge/releases/download/${CUSTOM_MAMBA_VERSION}/Miniforge3-${CUSTOM_MAMBA_VERSION}-$(uname)-$(uname -m).sh -o mamba_install.sh && \
    bash mamba_install.sh -b -p /opt/conda && \
    rm mamba_install.sh && \
    /opt/conda/bin/conda init bash && \
    /opt/conda/bin/mamba shell init --shell bash

# Add conda to PATH at the end so system Python 3.10 takes precedence
# Users can still activate conda environments when needed
ENV PATH="$PATH:/opt/conda/bin"

# install pipenv and gws dependencies system-wide (as root)
RUN pip install pipenv==2025.0.4 \
                click==8.3.1 \
                GitPython==3.1.45 \
                requests==2.32.5

# Create non-root user matching host ubuntu user
ARG USER_ID=1000
ARG GROUP_ID=1000

# Create group and user, then change ownership of necessary directories
RUN groupadd -g ${GROUP_ID} labuser && \
    useradd -m -u ${USER_ID} -g ${GROUP_ID} -s /bin/bash labuser && \
    echo "labuser ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

USER labuser
WORKDIR /home/labuser

# Add user's local bin to PATH for any user-installed packages
ENV PATH="/home/labuser/.local/bin:${PATH}"


COPY --chown=labuser:labuser ./init /init-lab

RUN chmod +x /init-lab/entrypoint.sh && \
    sed -i -e 's/\r$//' /init-lab/entrypoint.sh && \
    sed -i -e 's/\r$//' /init-lab/init_lab.sh && \
    sed -i -e 's/\r$//' /init-lab/clean.sh

EXPOSE 3000

ENTRYPOINT [ "/init-lab/entrypoint.sh" ]
CMD [ "--run-glab" ]
