#!/bin/bash
set -e

# start labs
if [ "$1" == "--run-glab" ]; then
    # gws lab
    # default port=3000, ip=0.0.0.0
    bash "/gpm/gpm.sh" 
    exec python3 "/lab/user/main/main/manage.py" --uri $LAB_URI --token $LAB_TOKEN --runserver --runmode $LAB_MODE
elif [ "$1" == "--run-jlab" ]; then
    # jupyter lab
    bash "/gpm/gpm.sh"
    export SHELL=/bin/bash
    exec jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --NotebookApp.iopub_data_rate_limit=1.0e10 --notebook-dir=$LAB_WORK_DIR --allow-root --NotebookApp.token=$LAB_TOKEN --NotebookApp.password=
elif [ "$1" == "--run-vlab" ]; then
    # vscode lab
    bash "/gpm/gpm.sh"
    export PASSWORD=${LAB_TOKEN}
    exec code-server --auth password --bind-addr 0.0.0.0:8080
else
    exec "$@"
fi
