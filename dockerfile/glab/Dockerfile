ARG IMAGE="ubuntu:20.04"
FROM $IMAGE
#FROM "ubuntu:20.04"
#FROM "nvidia/cuda:11.2.1-runtime-ubuntu20.04"

LABEL maintainer="Admin <admin@gencovery.com>"

# Set UTC timezone for the docker
ENV TZ=UTC

# don't name it PIP_VERSION because it will be overwritten by pip
ENV CUSTOM_PIP_VERSION 23.1.2
ENV CONDA_VERSION py38_23.3.1-0

# install python v 3.8 & base packages
RUN apt-get -y update && \
    apt-get -y install python3.8 python3-distutils && \
    apt-get -y install git curl zip unzip bzip2 wget rsync && \
    # It is needed to install hdmedians which is a dependency of scikit-bio
    apt-get -y install gcc libpq-dev python3-dev

# install pip 
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3 get-pip.py "pip==${CUSTOM_PIP_VERSION}" && \
    python3 -m pip install --upgrade setuptools 
# install pipenv
RUN pip install pipenv==2023.7.9

# install conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-${CONDA_VERSION}-Linux-x86_64.sh -O miniconda.sh && \
    # for arm64
    # wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-${CONDA_VERSION}-Linux-aarch64.sh -O miniconda.sh && \
    mkdir -p /opt && \
    sh miniconda.sh -b -p /opt/conda && \
    rm miniconda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc

# install gws dependencies
RUN python3 -m pip install  click==8.1.3 \
                            GitPython==3.1.26 \
                            requests==2.28.2
                            
EXPOSE 3000

COPY ./init /init-lab

RUN chmod +x /init-lab/entrypoint.sh && \
    sed -i -e 's/\r$//' /init-lab/entrypoint.sh && \
    sed -i -e 's/\r$//' /init-lab/init_lab.sh && \
    sed -i -e 's/\r$//' /init-lab/clean.sh

ENTRYPOINT [ "/init-lab/entrypoint.sh" ]
CMD [ "--run-glab" ]
