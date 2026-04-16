#!/bin/bash
set -e

ENTRYPOINT_SCRIPT="$0"
ENTRYPOINT_ARGS=("$@")
source /init-lab/align-user.sh
align_labuser_and_switch /lab /init-lab/codelab-init-ssh.sh

# Running as labuser from here on.
# If the container was started directly as labuser (via `user:` in compose),
# the hook above was skipped — run SSH init now via sudo.
if ! pgrep -x sshd >/dev/null 2>&1; then
    sudo -E bash /init-lab/codelab-init-ssh.sh
fi

bash /init-lab/init_lab.sh CODELAB
echo "Codelab environment is ready."

exec bash -c "${OPENVSCODE_SERVER_ROOT}/bin/openvscode-server --port 8080 --host 0.0.0.0 --without-connection-token"
