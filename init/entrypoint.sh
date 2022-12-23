#!/bin/bash
set -e

# start labs
if [ "$1" == "--run-glab" ]; then
    # glab
    # default port=3000, ip=0.0.0.0 
    bash /init-lab/gpm.sh GLAB
    exec bash -c "source /opt/conda/etc/profile.d/conda.sh && source /init-lab/clean.sh && python3 /lab/.sys/app/manage.py --runserver --runmode $LAB_MODE"
elif [ "$1" == "--run-codelab" ]; then
    # codelab
    bash "/init-lab/gpm.sh CODELAB"

    exec bash -c "source /init-lab/clean.sh && bash ${OPENVSCODE_SERVER_ROOT}/bin/openvscode-server --port 8080 --host 0.0.0.0 --without-connection-token"
elif [ "$1" == "--run-local" ]; then
    # mode to create a local dev environment where vscode can log in to the container
    bash "/init-lab/gpm.sh CODELAB"
    
    # prevent docker to stop 
    tail -f /dev/null
else
    exec "source /init-lab/clean.sh && $@"
fi
