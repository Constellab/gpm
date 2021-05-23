#!/bin/bash
set -e

if [ "$1" == "--runserver" ]; then
    if [ -n $2 ]; then
        LAB_NAME=$2
    fi

    # build and install dlib
    build_dir="/app/lab/.gws/externs/dlib-cpp/build"
    bash ./entrypoint/compile-dlib.sh $build_dir
    
    cd /app
    
    bash ./entrypoint/install-dep.sh
    
    cd /app
    
    # run server
    exec python3 "/app/lab/user/main/${LAB_NAME}/manage.py" --runserver --uri $LAB_URI --token $LAB_TOKEN --mode $LAB_START_MODE
else
    exec "$@"
fi
