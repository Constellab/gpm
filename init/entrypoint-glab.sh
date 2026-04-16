#!/bin/bash
set -e

ENTRYPOINT_SCRIPT="$0"
ENTRYPOINT_ARGS=("$@")
source /init-lab/align-user.sh
align_labuser_and_switch /lab

# Running as labuser from here on.

bash /init-lab/init_lab.sh GLAB
echo "Glab environment is ready."

exec bash -c "gws server run --settings-path /lab/.sys/app/settings.json"
