# Dockerfile to build an image to work on lab (gws_core, gws_biota)
# with vscode remote containers
ARG IMAGE="constellab/glab:latest"
FROM $IMAGE

USER labuser

# Configure python
RUN pip install mypy pylint autopep8

ENTRYPOINT [ "/init-lab/entrypoint.sh" ]
CMD [ "--run-local" ]
