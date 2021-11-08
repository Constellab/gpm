ARG IMAGE="glab:latest"
FROM $IMAGE

# Dockerfile from https://github.com/gitpod-io/openvscode-releases/blob/main/Dockerfile
ARG RELEASE_TAG=openvscode-server-v1.61.0

RUN apt update && \
    apt install -y git wget sudo && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /home

# Downloading the latest VSC Server release and extracting the release archive
RUN wget https://github.com/gitpod-io/openvscode-server/releases/download/${RELEASE_TAG}/${RELEASE_TAG}-linux-x64.tar.gz && \
    tar -xzf ${RELEASE_TAG}-linux-x64.tar.gz && \
    rm -f ${RELEASE_TAG}-linux-x64.tar.gz


RUN pip install mypy pylint autopep8

WORKDIR /lab/user/

COPY ./.vs-code-server-config/ /.vs-code-server-config/

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV HOME=/lab/user/
ENV EDITOR=code
ENV VISUAL=code
ENV GIT_EDITOR="code --wait"
ENV OPENVSCODE_SERVER_ROOT=/home/${RELEASE_TAG}-linux-x64

EXPOSE 8080

COPY ./entrypoint.sh /entrypoint.sh

RUN sed -i -e 's/\r$//' /entrypoint.sh
RUN sed -i -e 's/\r$//' /gpm/gpm.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "--run-codelab" ]

