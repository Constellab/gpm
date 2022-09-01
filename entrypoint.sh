#!/bin/bash
set -e

# start labs
if [ "$1" == "--run-glab" ]; then
    # glab
    # default port=3000, ip=0.0.0.0 
    bash "/gpm/gpm.sh" 
    exec bash -c "source /opt/conda/etc/profile.d/conda.sh && source /gpm/clean.sh && python3 /lab/.sys/app/manage.py --runserver --runmode $LAB_MODE"
elif [ "$1" == "--run-codelab" ]; then
    # codelab
    bash "/gpm/gpm.sh"

    if [ ! -d /lab/user/.vscode ]; then
      mkdir /lab/user/.vscode
      cp /.vs-code-server-config/launch.json /lab/user/.vscode/launch.json
      cp /.vs-code-server-config/extensions.json /lab/user/.vscode/extensions.json
      cp /.vs-code-server-config/settings.json /lab/user/.vscode/settings.json
    fi

    # copy the pylintrc file
    if [ ! -d /lab/user/.pylintrc ]; then
      cp /.vs-code-server-config/.pylintrc /lab/user/.pylintrc
    fi

    exec bash -c "source /gpm/clean.sh && bash ${OPENVSCODE_SERVER_ROOT}/bin/openvscode-server --port 8080 --host 0.0.0.0 --without-connection-token"
elif [ "$1" == "--run-local" ]; then
    bash "/gpm/gpm.sh"

    if [ ! -d /lab/user/.vscode ]; then
      mkdir /lab/user/.vscode
      cp /.vs-code-server-config/launch.json /lab/user/.vscode/launch.json
      cp /.vs-code-server-config/extensions.json /lab/user/.vscode/extensions.json
      cp /.vs-code-server-config/settings.json /lab/user/.vscode/settings.json
    fi

    # copy the pylintrc file
    if [ ! -d /lab/user/.pylintrc ]; then
      cp /.vs-code-server-config/.pylintrc /lab/user/.pylintrc
    fi
    
    # prevent docker to stop 
    tail -f /dev/null
else
    exec "source /gpm/clean.sh && $@"
fi
