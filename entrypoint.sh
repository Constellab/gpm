#!/bin/bash
set -e

#export SHELL="/bin/bash"

# start labs
if [ "$1" == "--run-glab" ]; then
    # glab
    # default port=3000, ip=0.0.0.0 
    bash "/gpm/gpm.sh" 
    exec bash -c "source /opt/conda/etc/profile.d/conda.sh" && python3 "/lab/.sys/app/manage.py" --uri $LAB_URI --token $LAB_TOKEN --runserver --runmode $LAB_MODE
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

    bash "${OPENVSCODE_SERVER_ROOT}/server.sh" --port 8080

elif [ "$1" == "--run-local" ]; then
    bash "/gpm/gpm.sh"
    # Prevent docker to stop 
    tail -f /dev/null
else
    exec "$@"
fi
