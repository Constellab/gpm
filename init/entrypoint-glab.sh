#!/bin/bash
set -e

# glab
# default port=3000, ip=0.0.0.0 
bash /init-lab/init_lab.sh GLAB
echo "Glab environment is ready."

# Use 'source' to run clean.sh in the current shell context, allowing it to unset
# sensitive environment variables before starting the server
exec bash -c "source /init-lab/clean.sh && gws server run --settings-path /lab/.sys/app/settings.json"
