
ARG IMAGE="glab:latest"
FROM $IMAGE

LABEL maintainer="Admin <admin@gencovery.com>"

ENV LAB_NAME main
ENV WORKDIR_DIR /gpm
ENV CONDA_VERSION latest

ADD ./ ${WORKDIR_DIR}
WORKDIR ${WORKDIR_DIR}

# install code-server for remote vscode
RUN curl -fsSL https://code-server.dev/install.sh | sh

# Create forlder for the vs code config
RUN mkdir -p ${USER}/.local/share/code-server/ && mkdir -p ${USER}/.local/share/code-server/User
# Add config for vs code
COPY ./.vs-code-server-config/settings.json /root/.local/share/code-server/User/settings.json 

# install code-server extensions
# Install jupyter extension
RUN code-server --install-extension ms-toolsai.jupyter
# instal manually python extension version 2020.10.332292344 because higher verison have problem with code-server
# https://github.com/cdr/code-server/issues/2341
RUN wget https://github.com/microsoft/vscode-python/releases/download/2020.10.332292344/ms-python-release.vsix \
 && code-server --install-extension ./ms-python-release.vsix || true

# Install git graph extension
RUN code-server --install-extension mhutchie.git-graph

EXPOSE 8080

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "--run-vlab" ]
