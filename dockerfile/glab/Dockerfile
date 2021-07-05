
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

# install python
RUN apt-get -y update
RUN apt-get -y install python3 python3-distutils
RUN apt-get -y install git curl zip unzip bzip2 wget

# install pip
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3 get-pip.py
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --upgrade setuptools

# install gws dependencies
RUN python3 -m pip install peewee fastapi uvicorn starlette-context
RUN python3 -m pip install sphinx sphinx-rtd-theme rinohtype
RUN python3 -m pip install passlib
RUN python3 -m pip install python-multipart
RUN python3 -m pip install aiofiles
RUN python3 -m pip install pyjwt
RUN python3 -m pip install itsdangerous
RUN python3 -m pip install awesome-slugify
RUN python3 -m pip install click
RUN python3 -m pip install psutil
RUN python3 -m pip install pymysql mysql-connector
RUN python3 -m pip install pylint mypy
RUN python3 -m pip install python-swiftclient

# install biota dependencies
RUN python3 -m pip install biopython

# install gaia dependencies
RUN python3 -m pip install tensorflow 
RUN python3 -m pip install torch torchvision torchaudio
RUN python3 -m pip install numpy<1.19.0,>=1.16.0
RUN python3 -m pip install scipy==1.7.0
RUN python3 -m pip install scikit-learn
RUN python3 -m pip install pandas
RUN python3 -m pip install matplotlib
RUN python3 -m pip install xlrd>=1.0.0
RUN python3 -m pip install dill
RUN python3 -m pip install cvxpy

# install conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-${CONDA_VERSION}-Linux-x86_64.sh -O miniconda.sh && \
    mkdir -p /opt && \
    sh miniconda.sh -b -p /opt/conda && \
    rm miniconda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc
    
# install bazel
RUN apt-get -y install gnupg
RUN curl -fsSL https://bazel.build/bazel-release.pub.gpg | gpg --dearmor > bazel.gpg
RUN mv bazel.gpg /etc/apt/trusted.gpg.d/
RUN echo "deb [arch=amd64] https://storage.googleapis.com/bazel-apt stable jdk1.8" | tee /etc/apt/sources.list.d/bazel.list
RUN apt -y update && apt -y install bazel
RUN apt -y update && apt -y full-upgrade

# install C++ dev tools
RUN apt-get -y install g++ unzip zip
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install build-essential cmake pkg-config
RUN apt-get -y install libx11-dev libatlas-base-dev
RUN apt-get -y install libgtk-3-dev libboost-python-dev
RUN apt-get -y install libopenblas-dev liblapack-dev

# install R
RUN apt-get -y install r-base

# install mariadb client, rsync
RUN apt-get -y install mariadb-client
RUN apt-get -y install rsync

EXPOSE 3000

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "--run-glab" ]
