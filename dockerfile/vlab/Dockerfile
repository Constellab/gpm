ARG IMAGE="glab:latest"
FROM $IMAGE

LABEL maintainer="Admin <admin@gencovery.com>"

ENV LAB_NAME main
ENV WORKDIR_DIR /gpm
ENV CONDA_VERSION latest

ADD ./ ${WORKDIR_DIR}
WORKDIR ${WORKDIR_DIR}

# install jupyter lab
RUN python3 -m pip install jupyterlab && \
    python3 -m pip install ipywidgets
    
# install code-server for remote vscode
RUN curl -fsSL https://code-server.dev/install.sh | sh && \
    mkdir -p ${USER}/.local/share/code-server/ && mkdir -p ${USER}/.local/share/code-server/User

# Add config for vs code
COPY ./.vs-code-server-config/settings.json /root/.local/share/code-server/User/settings.json 

# install python (including jupyter), git graph extension
RUN code-server --install-extension ms-python.python && \
    code-server --install-extension mhutchie.git-graph

EXPOSE 8080

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "--run-vlab" ]
