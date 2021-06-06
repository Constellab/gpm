#!/bin/bash
set -e
if [ "$1" == "--runserver" ]; then
    # install lab
    bash "/app/lab/.gws/bricks/gws/gpm.sh"

    # run server
    exec python3 "/app/lab/user/main/main/manage.py" --uri $LAB_URI --token $LAB_TOKEN --runserver --runmode "prod"
else
    exec "$@"
fi
