# Dockerfile to build an image to work on lab (gws_core, gws_biota)
# with vscode remote containers
ARG IMAGE="constellab/glab:latest"
FROM $IMAGE


USER labuser

# Configure python
RUN pip install ruff

RUN mkdir -p /home/labuser/.ssh

USER root

# Duplicate of glab but it is useful to have it here for clarity and cache control
COPY --chown=labuser:labuser ./init /init-lab

RUN chmod +x /init-lab/entrypoint-local-dev-env.sh && \
    sed -i -e 's/\r$//' /init-lab/entrypoint-local-dev-env.sh && \
    sed -i -e 's/\r$//' /init-lab/init_lab.sh && \
    sed -i -e 's/\r$//' /init-lab/clean.sh

USER labuser

ENTRYPOINT [ "/init-lab/entrypoint-local-dev-env.sh" ]
