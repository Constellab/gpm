#!/bin/bash
set -e

# glab
# default port=3000, ip=0.0.0.0 
bash /init-lab/init_lab.sh GLAB
echo "Glab environment is ready."

# Start gws server
exec bash -c "gws server run --settings-path /lab/.sys/app/settings.json"
