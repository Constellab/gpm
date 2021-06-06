#!/bin/sh

set -e

# install labs
if [ "$1" == "--runserver" ]; then
    # gws lab
    bash "/gpm/gpm.sh" 
    exec python3 "/app/lab/user/main/main/manage.py" --uri $LAB_URI --token $LAB_TOKEN --runserver --runmode "prod"
elif [ "$1" == "--runjlab" ]; then
    # jupiter la
    bash "/app/gpm/gpm.sh"
    export SHELL=/bin/bash
    exec jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --notebook-dir=${LAB_WORK_DIR} --allow-root --NotebookApp.token=${LAB_TOKEN} --NotebookApp.password=
    exec "$@"
elif [ "$1" == "--runvlab" ]; then
    # vscode lab
    bash "/app/gpm/gpm.sh"
    export PASSWORD=${LAB_TOKEN}
    exec code-server --auth password --bind-addr 0.0.0.0:8080
else
    exec "$@"
fi
