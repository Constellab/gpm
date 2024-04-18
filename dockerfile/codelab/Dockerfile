ARG IMAGE="glab:latest"
FROM $IMAGE

LABEL maintainer="Admin <admin@gencovery.com>"

# Choose version from https://github.com/gitpod-io/openvscode-server
ARG RELEASE_TAG=openvscode-server-v1.88.0
ARG RELEASE_ORG="gitpod-io"
ARG OPENVSCODE_SERVER_ROOT="/home/.openvscode-server"

# Dockerfile from https://github.com/gitpod-io/openvscode-releases/blob/main/Dockerfile
WORKDIR /home

RUN apt update && \
    apt install -y git wget && \
    rm -rf /var/lib/apt/lists/* && \
    pip install mypy==1.9.0 pylint==3.1.0 autopep8==2.1.0

# Set UTC timezone for the docker
ENV TZ=UTC \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    EDITOR=code \
    VISUAL=code \
    GIT_EDITOR="code --wait" \
    OPENVSCODE_SERVER_ROOT=${OPENVSCODE_SERVER_ROOT}


# Downloading the latest VSC Server release and extracting the release archive
# Rename `openvscode-server` cli tool to `code` for convenience
RUN if [ -z "${RELEASE_TAG}" ]; then \
        echo "The RELEASE_TAG build arg must be set." >&2 && \
        exit 1; \
    fi && \
    arch=$(uname -m) && \
    if [ "${arch}" = "x86_64" ]; then \
        arch="x64"; \
    elif [ "${arch}" = "aarch64" ]; then \
        arch="arm64"; \
    elif [ "${arch}" = "armv7l" ]; then \
        arch="armhf"; \
    fi && \
    wget https://github.com/${RELEASE_ORG}/openvscode-server/releases/download/${RELEASE_TAG}/${RELEASE_TAG}-linux-${arch}.tar.gz && \
    tar -xzf ${RELEASE_TAG}-linux-${arch}.tar.gz && \
    mv -f ${RELEASE_TAG}-linux-${arch} ${OPENVSCODE_SERVER_ROOT} && \
    cp ${OPENVSCODE_SERVER_ROOT}/bin/remote-cli/openvscode-server ${OPENVSCODE_SERVER_ROOT}/bin/remote-cli/code && \
    rm -f ${RELEASE_TAG}-linux-${arch}.tar.gz

WORKDIR /lab/user/

COPY ./.vs-code-server-config/ /.vs-code-server-config/

EXPOSE 8080

ENTRYPOINT [ "/init-lab/entrypoint.sh" ]
CMD [ "--run-codelab" ]

