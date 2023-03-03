# Dockerfile to build an image to work on lab (gws_core, gws_biota)
# with vscode remote containers
FROM glab-local

# Configure python
RUN pip install mypy pylint autopep8

# copy the example config.json
COPY ./dockerfile/dev-env/config.json /conf/config.json

COPY ./.vs-code-server-config/ /.vs-code-server-config/



ENTRYPOINT [ "/init-lab/entrypoint.sh" ]
CMD [ "--run-local" ]
