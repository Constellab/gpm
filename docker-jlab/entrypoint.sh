#!/bin/bash
set -e
token=""
if [ "$1" == "--runserver" ]; then
    if [ -n "$JLAB_TOKEN" ]; then
        token=$JLAB_TOKEN
    fi

    # install dependencies
    find /app/gws/gws/bricks -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
    find /app/gws/gws/sandbox -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
    find /app/gws/gws/labs -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
    find /app/gws/user/bricks -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
    find /app/gws/user/sandbox -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
    find /app/gws/user/labs -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;

    # run server
    exec jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --notebook-dir=/app/gws/user/ --allow-root --NotebookApp.tokenUnicode=$token
else
    exec "$@"
fi
