# Dockerfile to build an image for local lab development.
# Mirrors codelab's env propagation and UID alignment without OpenVSCode-server
# or SSH — connect via VS Code's "Attach to running container" Dev Containers flow.

ARG IMAGE="constellab/glab:latest"
FROM $IMAGE

LABEL maintainer="Admin <admin@gencovery.com>"

ENV TZ=UTC \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    INIT_LAB_PATH=/init-lab

USER root
WORKDIR /home

# Install ruff and pyright into the glab venv. Must run as labuser because root can't
# write to the labuser-owned venv at /home/labuser/.venv.
USER labuser
RUN uv pip install --no-cache ruff pyright
USER root

COPY --chown=labuser:labuser ./init ${INIT_LAB_PATH}

RUN chmod +x ${INIT_LAB_PATH}/entrypoint-local-dev-env.sh \
              ${INIT_LAB_PATH}/setup-shell-env.sh

# Default to labuser; sub-composes that need root for UID alignment on
# bind-mounts can override with `user: "0:0"`.
USER labuser
WORKDIR /lab/user/

ENTRYPOINT [ "/init-lab/entrypoint-local-dev-env.sh" ]
