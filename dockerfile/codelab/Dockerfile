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
RUN curl -fsSL https://code-server.dev/install.sh | sh -s -- --version=3.11.1 && \
    mkdir -p ${USER}/.local/share/code-server/ && mkdir -p ${USER}/.local/share/code-server/User

# Add config for vs code
COPY ./.vs-code-server-config/settings.json /root/.local/share/code-server/User/settings.json 
COPY ./.vs-code-server-config/keybindings.json /root/.local/share/code-server/User/keybindings.json 

# install VS code extensions : jupyter v2021.6.999660014, python v 2021.8.1159798656, git graph
# Compatible version https://github.com/cdr/code-server/issues/3874#issuecomment-923383398
RUN code-server --install-extension ms-toolsai.jupyter && \
    wget https://storage.sbg.cloud.ovh.net/v1/AUTH_a0286631d7b24afba3f3cdebed2992aa/public/ms-toolsai-jupyter-2021.6.999660014.vsix && \
    code-server --install-extension ./ms-toolsai-jupyter-2021.6.999660014.vsix || true && \
    wget https://open-vsx.org/api/ms-python/python/2021.8.1159798656/file/ms-python.python-2021.8.1159798656.vsix && \
    code-server --install-extension ./ms-python.python-2021.8.1159798656.vsix || true && \
    code-server --install-extension mhutchie.git-graph


EXPOSE 8080

COPY ./entrypoint.sh /entrypoint.sh

RUN sed -i -e 's/\r$//' /entrypoint.sh
RUN sed -i -e 's/\r$//' /gpm/gpm.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "--run-codelab" ]
