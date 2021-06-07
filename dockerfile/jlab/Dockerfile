
ARG IMAGE="glab:latest"
FROM $IMAGE

LABEL maintainer="Admin <admin@gencovery.com>"

ENV LAB_NAME main
ENV WORKDIR_DIR /gpm
ENV CONDA_VERSION latest

ADD ./ ${WORKDIR_DIR}
WORKDIR ${WORKDIR_DIR}

# install jupyter lab
RUN python3 -m pip install jupyterlab
RUN python3 -m pip install ipywidgets

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "--run-jlab" ]