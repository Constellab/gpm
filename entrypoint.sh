#!/bin/bash
set -e
if [ "$1" == "--runserver" ]; then
    lab_name=$2
    lab_uri=""
    lab_token=""
    
    if [ -n "$LAB_NAME" ]; then
        lab_name=$LAB_NAME
    fi

    if [ -n "$LAB_TOKEN" -a "$LAB_TOKEN" != "" ]; then
        lab_token="--lab-token $LAB_TOKEN"
    fi

    if [ -n "$LAB_URI" ]; then
        lab_uri="--lab-uri $LAB_URI"
    fi

    if [ -n "$START_MODE" -a "$START_MODE" = "--dev" ]; then
        start_mode="--demo"
    fi
    
    # build and install dlib
    build_dir="/app/gws/.gws/externs/dlib-cpp/build-gws"
    if [ ! -d "$build_dir" ]; then
        mkdir -p $build_dir
        cd $build_dir
        cmake -DUSE_AVX_INSTRUCTIONS=ON -DBUILD_SHARED_LIBS=1 ..
        cmake --build . --config Release
        make
    else
        cd $build_dir
    fi
    make install
    ldconfig
    cd /app

    # install dependencies
    find /app/gws/.gws/bricks -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
    find /app/gws/.gws/sandbox -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
    find /app/gws/.gws/labs -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
    find /app/gws/user/bricks -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
    find /app/gws/user/sandbox -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
    find /app/gws/user/labs -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;

    # run server
    exec python3 "/app/gws/user/labs/${lab_name}/manage.py" --runserver $lab_uri $lab_token $start_mode
else
    exec "$@"
fi
