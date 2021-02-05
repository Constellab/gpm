#!/bin/bash
set -e
token=""
home_dir=""
biodata_vesion="latest"
if [ "$1" == "--runserver" ]; then
    if [ -n "$JLAB_TOKEN" ]; then
        token=$JLAB_TOKEN
    fi

    if [ -n "$JLAB_HOME_DIR" ]; then
        home_dir=$JLAB_HOME_DIR
    fi

    if [ -n "$BIODATA_VERSION" ]; then
        biodata_vesion=$BIODATA_VERSION
    fi

    # build and install dlib
    build_dir="/app/gws/.gws/externs/dlib-cpp/build-jlab"
    if [ ! -d "$build_dir" ]; then
        mkdir -p $build_dir
        cd $build_dir
        cmake -DUSE_AVX_INSTRUCTIONS=ON -DBUILD_SHARED_LIBS=1 ..
        cmake --build . --config Release
        make
    else
        cd $build_dir
    fi
    cd $build_dir
    make install
    ldconfig
    cd /app

    # install dependencies
    find /app/gws/.gws/bricks -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
    find /app/gws/.gws/sandbox -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
    find /app/gws/user/bricks -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
    find /app/gws/user/sandbox -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;

    # create symbolic link to biodata
    if [ ! -d "/app/gws/.gws/data/biota" ]; then
        if [ -d "/mnt/biodata/prod/biota/${biodata_vesion}/" ]; then
            ln -s /mnt/biodata/prod/biota/${biodata_vesion}/ /app/gws/.gws/data/biota
        fi
    fi

    # run server
    export SHELL=/bin/bash
    exec jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --notebook-dir=${home_dir} --allow-root --NotebookApp.token=${token} --NotebookApp.password=
else
    exec "$@"
fi
