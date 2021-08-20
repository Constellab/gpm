ARG IMAGE="ubuntu:20.04"
FROM $IMAGE
#FROM "ubuntu:20.04"
#FROM "nvidia/cuda:11.2.1-runtime-ubuntu20.04"

LABEL maintainer="Admin <admin@gencovery.com>"

ENV LAB_NAME main
ENV WORKDIR_DIR /gpm
ENV CONDA_VERSION latest

ADD ./ ${WORKDIR_DIR}
WORKDIR ${WORKDIR_DIR}

# install python & base packages
RUN apt-get -y update && \
    apt-get -y install python3 python3-distutils && \
    apt-get -y install git curl zip unzip bzip2 wget rsync && \
    apt-get -y install pipenv

# install pip
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3 get-pip.py && \
    python3 -m pip install --upgrade pip && \
    python3 -m pip install --upgrade setuptools
    
# install bazel
RUN apt-get -y install gnupg && \
    curl -fsSL https://bazel.build/bazel-release.pub.gpg | gpg --dearmor > bazel.gpg && \
    mv bazel.gpg /etc/apt/trusted.gpg.d/ && \
    echo "deb [arch=amd64] https://storage.googleapis.com/bazel-apt stable jdk1.8" | tee /etc/apt/sources.list.d/bazel.list && \
    apt -y update && \
    apt -y install bazel && \
    apt -y full-upgrade

# install C++ dev tools
RUN apt-get -y install g++ unzip zip && \
    DEBIAN_FRONTEND="noninteractive" apt-get -y install build-essential cmake pkg-config && \
    apt-get -y install libx11-dev libatlas-base-dev && \
    apt-get -y install libgtk-3-dev libboost-python-dev && \
    apt-get -y install libopenblas-dev liblapack-dev

# install conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-${CONDA_VERSION}-Linux-x86_64.sh -O miniconda.sh && \
    mkdir -p /opt && \
    sh miniconda.sh -b -p /opt/conda && \
    rm miniconda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc
    
# install gws dependencies
RUN python3 -m pip install twine && \
    python3 -m pip install peewee fastapi uvicorn starlette-context && \
    python3 -m pip install sphinx sphinx-rtd-theme rinohtype && \
    python3 -m pip install passlib && \
    python3 -m pip install python-multipart && \
    python3 -m pip install aiofiles && \
    python3 -m pip install pyjwt && \
    python3 -m pip install itsdangerous && \
    python3 -m pip install awesome-slugify && \
    python3 -m pip install click && \
    python3 -m pip install psutil && \
    python3 -m pip install pymysql mysql-connector && \
    python3 -m pip install pylint mypy 
    #&& \
    #python3 -m pip install python-swiftclient

# install biota dependencies
RUN python3 -m pip install biopython

# install gaia dependencies
RUN python3 -m pip install tensorflow && \
    python3 -m pip install torch torchvision torchaudio && \
    python3 -m pip install numpy && \
    python3 -m pip install pandas && \
    python3 -m pip install matplotlib && \
    python3 -m pip install scipy>=1.7.0 && \
    python3 -m pip install scikit-learn && \
    python3 -m pip install xlrd>=1.0.0 && \
    python3 -m pip install dill && \
    python3 -m pip install cvxpy

# other installs (R, mariadb-client, etc.)
RUN apt-get -y install mariadb-client

EXPOSE 3000

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "--run-glab" ]
