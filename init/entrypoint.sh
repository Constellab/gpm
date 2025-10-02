#!/bin/bash
set -e

# start labs
if [ "$1" == "--run-glab" ]; then
    # glab
    # default port=3000, ip=0.0.0.0 
    bash /init-lab/init_lab.sh GLAB
    echo "Glab environment is ready."
    exec bash -c "source /init-lab/clean.sh && gws server run --settings-path /lab/.sys/app/settings.json"
elif [ "$1" == "--run-codelab" ]; then
    # Source the conda and mamba profiles
    # This is necessary to ensure conda and mamba commands are available in the environment
    # otherwise the codelab-init-ssh.sh breaks the 'bash -c "mamba"' command.
    source /opt/conda/etc/profile.d/conda.sh
    source /opt/conda/etc/profile.d/mamba.sh

    sudo bash /init-lab/codelab-init-ssh.sh
    
    # codelab
    bash /init-lab/init_lab.sh CODELAB
    
    echo "Codelab environment is ready."

    exec bash -c "source /init-lab/clean.sh && ${OPENVSCODE_SERVER_ROOT}/bin/openvscode-server --port 8080 --host 0.0.0.0 --without-connection-token"
elif [ "$1" == "--run-local" ]; then
    # mode to create a local dev environment where vscode can log in to the container
    bash /init-lab/init_lab.sh CODELAB

    echo "Dev environment is ready."
    
    # prevent docker to stop 
    tail -f /dev/null
else
    echo "Invalid argument: $1"
    exec "source /init-lab/clean.sh && $@"
fi

