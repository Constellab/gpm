#!/bin/bash
set -e

# start labs
if [ "$1" == "--run-glab" ]; then
    # glab
    # default port=3000, ip=0.0.0.0 
    bash "/gpm/gpm.sh" 
    exec python3 "/lab/.sys/app/manage.py" --uri $LAB_URI --token $LAB_TOKEN --runserver --runmode $LAB_MODE
elif [ "$1" == "--run-notelab" ]; then
    # notelab (jupyter)
    # bash "/gpm/gpm.sh" /!\ Do not reinstall packages
    if [[ ! -n $JLAB_TYPE ]]; then
        export JLAB_TYPE="notebook"
    fi
    export SHELL=/bin/bash
    exec jupyter $JLAB_TYPE --ip=0.0.0.0 --port=8888 --no-browser --NotebookApp.iopub_data_rate_limit=1.0e10 --notebook-dir=/lab/user/notebooks --allow-root --NotebookApp.token=$LAB_TOKEN --NotebookApp.password=
elif [ "$1" == "--run-codelab" ]; then
    # codelab
    bash "/gpm/gpm.sh"
    export PASSWORD=${LAB_TOKEN}
    exec code-server --auth password --bind-addr 0.0.0.0:8080
else
    exec "$@"
fi
