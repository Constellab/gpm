#!/bin/bash
set -e

ENTRYPOINT_SCRIPT="$0"
ENTRYPOINT_ARGS=("$@")
source /init-lab/align-user.sh
align_labuser_and_switch "${LAB_FOLDER}" /init-lab/codelab-root-init.sh

# Running as labuser from here on.
# If the container was started directly as labuser (via `user:` in compose),
# the hook above was skipped — run the root init now via sudo.
if [ ! -f /run/codelab-root-init-done ]; then
    sudo -E bash /init-lab/codelab-root-init.sh
fi

# Configure shell env (~/.bashrc_docker_env) so VS Code integrated terminals get
# the Dockerfile's PATH/VIRTUAL_ENV. init-ssh.sh also does this for SSH login
# shells; this call keeps it working when the SSH server is disabled.
bash /init-lab/setup-shell-env.sh

bash /init-lab/init_lab.sh CODELAB
echo "Codelab environment is ready."

exec bash -c "${OPENVSCODE_SERVER_ROOT}/bin/openvscode-server --port 8080 --host 0.0.0.0 --without-connection-token"
