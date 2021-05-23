#!/bin/bash
set -e

if [ "$1" == "--runserver" ]; then
    
    # build and install dlib
    build_dir="/app/lab/.gws/externs/dlib-cpp/build"
    bash ./entrypoint/compile-dlib.sh $build_dir
    
    cd /app

    bash ./entrypoint/install-dep.sh
    
    cd /app
    
    # run server
    export SHELL=/bin/bash
    exec jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --notebook-dir=${LAB_WORK_DIR} --allow-root --NotebookApp.token=${LAB_TOKEN} --NotebookApp.password=
else
    exec "$@"
fi
