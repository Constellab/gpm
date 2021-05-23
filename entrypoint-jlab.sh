#!/bin/bash
set -e

if [ "$1" == "--runserver" ]; then
    
    # install dlib and custom brick dependencies
    bash /entrypoint-install-dep.sh

    # run server
    export SHELL=/bin/bash
    exec jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --notebook-dir=${LAB_WORK_DIR} --allow-root --NotebookApp.token=${LAB_TOKEN} --NotebookApp.password=
    
else
    exec "$@"
fi
