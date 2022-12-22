#!/bin/bash
set -e

# start labs
if [ "$1" == "--run-glab" ]; then
    # glab
    # default port=3000, ip=0.0.0.0 
    bash "/gpm/gpm.sh GLAB" 
    exec bash -c "source /opt/conda/etc/profile.d/conda.sh && source /gpm/clean.sh && python3 /lab/.sys/app/manage.py --runserver --runmode $LAB_MODE"
elif [ "$1" == "--run-codelab" ]; then
    # codelab
    bash "/gpm/gpm.sh CODELAB"

    exec bash -c "source /gpm/clean.sh && bash ${OPENVSCODE_SERVER_ROOT}/bin/openvscode-server --port 8080 --host 0.0.0.0 --without-connection-token"
elif [ "$1" == "--run-local" ]; then
    # mode to create a local dev environment where vscode can log in to the container
    bash "/gpm/gpm.sh CODELAB"
    
    # prevent docker to stop 
    tail -f /dev/null
else
    exec "source /gpm/clean.sh && $@"
fi
