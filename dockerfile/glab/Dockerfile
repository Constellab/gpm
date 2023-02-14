ARG IMAGE="ubuntu:20.04"
FROM $IMAGE
#FROM "ubuntu:20.04"
#FROM "nvidia/cuda:11.2.1-runtime-ubuntu20.04"

LABEL maintainer="Admin <admin@gencovery.com>"

# Set UTC timezone for the docker
ENV TZ=UTC

ENV CONDA_VERSION py39_4.10.3
#ENV CONDA_VERSION latest

RUN df -H

# install python v 3.8 & base packages
RUN apt-get -y update && \
    apt-get -y install jq && \
    apt-get -y install python3.8 python3-distutils && \
    apt-get -y install git curl zip unzip bzip2 wget rsync && \
    apt-get -y install pipenv

RUN df -H

# install pip v 23.0
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3 get-pip.py "pip==23.0" && \
    python3 -m pip install --upgrade setuptools
RUN df -H
# install conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-${CONDA_VERSION}-Linux-x86_64.sh -O miniconda.sh && \
    mkdir -p /opt && \
    sh miniconda.sh -b -p /opt/conda && \
    rm miniconda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc

RUN df -H
# install gws dependencies
RUN python3 -m pip install  aiofiles==0.8.0 \
                            awesome-slugify==1.6.5 \
                            click==8.0.3 \
                            cryptography==36.0.1 \
                            fastapi==0.91.0 \
                            GitPython==3.1.26 \
                            itsdangerous==2.0.1 \
                            mysql-connector==2.2.9 \
                            passlib==1.7.4 \
                            peewee==3.15.4 \
                            psutil==5.9.0 \
                            pyjwt==2.3.0 \
                            pymysql==1.0.2 \
                            python-multipart==0.0.5 \
                            requests==2.27.1 \
                            starlette-context==0.3.3 \
                            twine==3.7.1 \
                            uvicorn==0.20.0 \
                            charset-normalizer==2.0.12

RUN df -H
# install gaia dependencies
RUN python3 -m pip install  cvxpy==1.1.18 \
                            dill==0.3.4 \
                            numpy==1.24.1 \
                            pandas==1.5.2 \
                            matplotlib==3.6.2 \
                            scipy==1.10.0 \
                            scikit-learn==1.2.0
RUN df -H
EXPOSE 3000

COPY ./init /init-lab
RUN chmod +x /init-lab/entrypoint.sh

RUN sed -i -e 's/\r$//' /init-lab/entrypoint.sh && \
    sed -i -e 's/\r$//' /init-lab/init_lab.sh && \
    sed -i -e 's/\r$//' /init-lab/clean.sh

ENTRYPOINT [ "/init-lab/entrypoint.sh" ]
CMD [ "--run-glab" ]
