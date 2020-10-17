#!/bin/bash
set -e
if [ "$1" == "--runserver" ]; then
    lab_name=$2

    if [ -n "$LAB_NAME" ]; then
        lab_name=$LAB_NAME
    fi

    if [ -n "$START_MODE" -a "$START_MODE" = "--dev" ]; then
        start_mode="--demo"
    fi

    # install dependencies
    find /app/gws/gws/bricks -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
    find /app/gws/gws/sandbox -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
    find /app/gws/gws/labs -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
    find /app/gws/user/bricks -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
    find /app/gws/user/sandbox -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
    find /app/gws/user/labs -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;

    # run server
    exec python3 "/app/gws/user/labs/${lab_name}/manage.py" --runserver $start_mode
else
    exec "$@"
fi
