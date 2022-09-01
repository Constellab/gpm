ARG IMAGE="ubuntu:20.04"
FROM $IMAGE
#FROM "ubuntu:20.04"
#FROM "nvidia/cuda:11.2.1-runtime-ubuntu20.04"

LABEL maintainer="Admin <admin@gencovery.com>"

# Set UTC timezone for the docker
ENV TZ=UTC

ENV LAB_NAME app
ENV WORKDIR_DIR /gpm
ENV CONDA_VERSION py39_4.10.3
#ENV CONDA_VERSION latest

ADD ./ ${WORKDIR_DIR}
WORKDIR ${WORKDIR_DIR}

# install python v 3.8 & base packages
RUN apt-get -y update && \
    apt-get -y install jq && \
    apt-get -y install python3.8 python3-distutils && \
    apt-get -y install git curl zip unzip bzip2 wget rsync && \
    apt-get -y install pipenv

# install pip v 22.2.2
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3 get-pip.py "pip==22.2.2" && \
    python3 -m pip install --upgrade setuptools

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

# install jdk
RUN apt -y install default-jdk

# install gws dependencies
RUN python3 -m pip install  aiofiles==0.8.0 \
                            awesome-slugify==1.6.5 \
                            click==8.0.3 \
                            cryptography==36.0.1 \
                            fastapi==0.72.0 \
                            GitPython==3.1.26 \
                            itsdangerous==2.0.1 \
                            mysql-connector==2.2.9 \
                            passlib==1.7.4 \
                            peewee==3.14.8 \
                            psutil==5.9.0 \
                            pyjwt==2.3.0 \
                            pymysql==1.0.2 \
                            python-multipart==0.0.5 \
                            requests==2.27.1 \
                            starlette-context==0.3.3 \
                            twine==3.7.1 \
                            uvicorn==0.17.0 \
                            charset-normalizer==2.0.12

# install biota dependencies
RUN python3 -m pip install biopython==1.79

# install gaia dependencies
RUN python3 -m pip install  cvxpy==1.1.18 \
                            dill==0.3.4 \
                            numpy==1.22.1 \
                            pandas==1.3.5 \
                            matplotlib==3.5.1 \
                            scipy==1.8.0 \
                            scikit-learn==1.0.2 \
                            tensorflow==2.7.0
                            

# other installs (R, mariadb-client, etc.)
RUN apt-get -y install mariadb-client

EXPOSE 3000

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "--run-glab" ]
