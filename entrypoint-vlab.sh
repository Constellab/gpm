#!/bin/bash
set -e

if [ "$1" == "--runserver" ]; then
    
    # install dlib and custom brick dependencies
    bash /entrypoint-install-dep.sh
    
    vlab_app_dir="/app/lab/.sys/vlab/"
    if [ ! -d "$vlab_app_dir" ]; then
        mkdir -p $vlab_app_dir
    fi
    
    # run server
    export PASSWORD=${LAB_TOKEN}
    exec code-server --auth password --bind-addr 0.0.0.0:8080 --user-data-dir $vlab_app_dir
    
else
    exec "$@"
fi
