ARG IMAGE="ubuntu:22.04"
FROM $IMAGE
#FROM "nvidia/cuda:11.2.1-runtime-ubuntu22.04"

LABEL maintainer="Admin <admin@gencovery.com>"

# Set UTC timezone for the docker
ENV TZ=UTC

# don't name it PIP_VERSION because it will be overwritten by pip
ENV CUSTOM_PIP_VERSION=25.0.1
ENV CUSTOM_MAMBA_VERSION=24.11.3-2

# install python v 3.10 & base packages
RUN apt-get -y update && \
    apt-get -y install python3.10 python3-distutils && \
    apt-get -y install git curl zip unzip bzip2 wget rsync && \
    # It is needed to install hdmedians which is a dependency of scikit-bio
    # build essential install g++ and gcc which are commonly needed
    apt-get -y install gcc libpq-dev python3-dev build-essential && \
    # create a symlink to python3 so python command will use python3
    ln -s $(which python3) /usr/local/bin/python

# install pip 
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3 get-pip.py "pip==${CUSTOM_PIP_VERSION}" && \
    python3 -m pip install --upgrade setuptools 
# install pipenv
RUN pip install pipenv==2024.4.1

# Installing conda and mamba
# Info from https://github.com/conda-forge/miniforge#mambaforge
RUN curl -L https://github.com/conda-forge/miniforge/releases/download/${CUSTOM_MAMBA_VERSION}/Miniforge3-${CUSTOM_MAMBA_VERSION}-$(uname)-$(uname -m).sh -o mamba_install.sh && \
    bash mamba_install.sh -b -p /opt/conda && \
    # enable conda and mamba in bash
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo ". /opt/conda/etc/profile.d/mamba.sh" >> ~/.bashrc && \
    rm mamba_install.sh

# install gws dependencies
RUN python3 -m pip install  click==8.1.7 \
                            GitPython==3.1.43 \
                            requests==2.32.3
                            
EXPOSE 3000

COPY ./init /init-lab

RUN chmod +x /init-lab/entrypoint.sh && \
    sed -i -e 's/\r$//' /init-lab/entrypoint.sh && \
    sed -i -e 's/\r$//' /init-lab/init_lab.sh && \
    sed -i -e 's/\r$//' /init-lab/clean.sh

ENTRYPOINT [ "/init-lab/entrypoint.sh" ]
CMD [ "--run-glab" ]
