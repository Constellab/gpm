#!/bin/bash
set -e

if [ "$1" == "--runserver" ]; then
    if [ -n $2 ]; then
        LAB_NAME=$2
    fi

    # install dlib and custom brick dependencies
    bash /entrypoint-install-dep.sh
    
    # run server
    exec python3 "/app/lab/user/main/${LAB_NAME}/manage.py" --runserver --uri $LAB_URI --token $LAB_TOKEN --mode $LAB_START_MODE
    
else
    exec "$@"
fi
