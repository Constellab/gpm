#!/bin/bash
set -e

if [ "$1" == "--runserver" ]; then
    
    # build and install dlib
    build_dir="/app/lab/.gws/externs/dlib-cpp/build"
    bash ./entrypoint/compile-dlib.sh $build_dir
    
    cd /app
    
    bash ./entrypoint/install-dep.sh
    
    cd /app
    
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
