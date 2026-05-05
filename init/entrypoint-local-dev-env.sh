#!/bin/bash
set -e

ENTRYPOINT_SCRIPT="$0"
ENTRYPOINT_ARGS=("$@")
source /init-lab/align-user.sh
align_labuser_and_switch "${LAB_FOLDER}"

# Running as labuser from here on.

# Configure shell env (~/.bashrc_docker_env) so VS Code integrated terminals
# get the Dockerfile's PATH/VIRTUAL_ENV and the venv prompt.
bash /init-lab/setup-shell-env.sh

bash /init-lab/init_lab.sh CODELAB

# Setup SSH for local dev environment
sudo chown -R labuser:labuser /home/labuser/.ssh

echo "Dev environment is ready."

exec tail -f /dev/null
