#!/bin/bash
set -e

ENTRYPOINT_SCRIPT="$0"
ENTRYPOINT_ARGS=("$@")
source /init-lab/align-user.sh
align_labuser_and_switch "${LAB_FOLDER}" /init-lab/init-ssh.sh

# Running as labuser from here on.
# If the container was started directly as labuser (via `user:` in compose),
# the hook above was skipped — run the SSH init now via sudo.
if [ ! -f /run/init-ssh-done ]; then
    sudo -E bash /init-lab/init-ssh.sh
fi

# Configure shell env (~/.bashrc_docker_env) so VS Code integrated terminals
# get the Dockerfile's PATH/VIRTUAL_ENV and the venv prompt.
bash /init-lab/setup-shell-env.sh

bash /init-lab/init_lab.sh CODELAB

# Client-side SSH keys (mounted from the host, used by git) — unrelated to the
# SSH *server* above, which only runs when ENABLE_SSH_SERVER is enabled.
sudo chown -R labuser:labuser /home/labuser/.ssh

echo "Dev environment is ready."

exec tail -f /dev/null
