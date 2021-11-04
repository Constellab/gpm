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
    while [[ ! -f "/lab/.sys/.CODELAB_INSTALLED" ]]; do
        echo "Waiting codelab install ..." 
        sleep 10
    done
    bash "/gpm/gpm.sh"
    rm -rf "/lab/.sys/.CODELAB_INSTALLED"

    if [[ ! -n $JLAB_TYPE ]]; then
        export JLAB_TYPE="notebook"
    fi
    export SHELL=/bin/bash
    exec jupyter $JLAB_TYPE --ip=0.0.0.0 --port=8888 --no-browser --NotebookApp.iopub_data_rate_limit=1.0e10 --notebook-dir=/lab/user/notebooks --allow-root --NotebookApp.token=$LAB_TOKEN --NotebookApp.password=
elif [ "$1" == "--run-codelab" ]; then
    # codelab
    bash "/gpm/gpm.sh"

    # add the vscode configs
    if [ ! -d /lab/user/.openvscode-server/Machine ]; then
      mkdir -p /lab/user/.openvscode-server/Machine
      cp /.vs-code-server-config/settings.json /lab/user/.openvscode-server/Machine/settings.json
    fi
    
    if [ ! -d /lab/user/.vscode ]; then
      mkdir /lab/user/.vscode 
      cp /.vs-code-server-config/launch.json /lab/user/.vscode/launch.json
      cp /.vs-code-server-config/extensions.json /lab/user/.vscode/extensions.json
    fi

    cd /lab/user

    bash "${OPENVSCODE_SERVER_ROOT}/server.sh" --port 8080

elif [ "$1" == "--run-local" ]; then
    bash "/gpm/gpm.sh"
    # Prevent docker to stop 
    tail -f /dev/null
else
    exec "$@"
fi
