#!/bin/bash
set -e
if [ "$1" == "--runserver" ]; then
    
    # install dlib and custom brick dependencies
    bash /entrypoint-install-dep.sh
    
    # run server
    export PASSWORD=${LAB_TOKEN}
    exec code-server --auth password --bind-addr 0.0.0.0:8080
else
    exec "$@"
fi
