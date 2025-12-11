#!/bin/bash
set -e

# glab
# default port=3000, ip=0.0.0.0 
bash /init-lab/init_lab.sh GLAB
echo "Glab environment is ready."

exec bash -c "source /init-lab/clean.sh && gws server run --settings-path /lab/.sys/app/settings.json"
