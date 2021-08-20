ARG IMAGE="glab:latest"
FROM $IMAGE

LABEL maintainer="Admin <admin@gencovery.com>"

ENV LAB_NAME main
ENV WORKDIR_DIR /gpm
ENV CONDA_VERSION latest

ADD ./ ${WORKDIR_DIR}
WORKDIR ${WORKDIR_DIR}

# install jupyter lab, autopep8, mypy, pylint (dependencies for dev)
RUN python3 -m pip install jupyterlab && \
    python3 -m pip install ipywidgets && \
    python3 -m pip install mypy && \
    python3 -m pip install autopep8 && \
    python3 -m pip install pylint

# install code-server for remote vscode
RUN curl -fsSL https://code-server.dev/install.sh | sh && \
    mkdir -p ${USER}/.local/share/code-server/ && mkdir -p ${USER}/.local/share/code-server/User

# Add config for vs code
COPY ./.vs-code-server-config/settings.json /root/.local/share/code-server/User/settings.json 
COPY ./.vs-code-server-config/keybindings.json /root/.local/share/code-server/User/keybindings.json 

# install VS code extensions : jupyter, python, git graph
# RUN code-server --install-extension ms-toolsai.jupyter && \
#     code-server --install-extension ms-python.python && \
#     code-server --install-extension mhutchie.git-graph

# install code-server, jupyter, python, git graph extension
# install manually python extension version 2020.10.332292344 because higher verison have problem with code-server
# https://github.com/cdr/code-server/issues/2341
RUN code-server --install-extension ms-toolsai.jupyter && \
    wget https://github.com/microsoft/vscode-python/releases/download/2020.10.332292344/ms-python-release.vsix && \
    code-server --install-extension ./ms-python-release.vsix || true && \
    code-server --install-extension mhutchie.git-graph

EXPOSE 8080

COPY ./entrypoint.sh /entrypoint.sh

RUN sed -i -e 's/\r$//' /entrypoint.sh
RUN sed -i -e 's/\r$//' /gpm/gpm.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "--run-vlab" ]
