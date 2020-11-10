#!/bin/bash
set -e
token=""
home_dir=""
if [ "$1" == "--runserver" ]; then
    if [ -n "$JLAB_TOKEN" ]; then
        token=$JLAB_TOKEN
    fi

    if [ -n "$JLAB_HOME_DIR" ]; then
        home_dir=$JLAB_HOME_DIR
    fi

    # install dependencies
    find /app/gws/gws/bricks -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
    find /app/gws/gws/sandbox -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
    find /app/gws/gws/labs -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
    find /app/gws/user/bricks -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
    find /app/gws/user/sandbox -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
    find /app/gws/user/labs -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;

    # run server
    exec jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --notebook-dir=${home_dir} --allow-root --NotebookApp.token=${token} --NotebookApp.password=
else
    exec "$@"
fi
