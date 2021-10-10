#!/bin/bash
set -e

# start labs
if [ "$1" == "--run-glab" ]; then
    # gws lab
    # default port=3000, ip=0.0.0.0
    bash "/gpm/gpm.sh" 
    exec python3 "/lab/.sys/app/manage.py" --uri $LAB_URI --token $LAB_TOKEN --runserver --runmode $LAB_MODE
elif [ "$1" == "--run-clab" ]; then
    # vscode lab
    bash "/gpm/gpm.sh"
    export PASSWORD=${LAB_TOKEN}
    exec code-server --auth password --bind-addr 0.0.0.0:8080
else
    exec "$@"
fi
