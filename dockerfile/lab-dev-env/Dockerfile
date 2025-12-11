# Dockerfile to build an image to work on lab (gws_core, gws_biota)
# with vscode remote containers
ARG IMAGE="constellab/glab:latest"
FROM $IMAGE

USER labuser

ENTRYPOINT [ "/init-lab/entrypoint.sh" ]
CMD [ "--run-local" ]
