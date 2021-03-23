#!/bin/bash
set -e

if [ "$1" == "--runserver" ]; then
    
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

    # install ubuntu packages
    for path in `find /app/gws/.gws/ -mindepth 1 -maxdepth 4 -name 'requirements-apt.txt'`; do
        cat $path | xargs apt-get install -y
    done

    for path in `find /app/gws/user/ -mindepth 1 -maxdepth 4 -name 'requirements-apt.txt'`; do
        cat $path | xargs apt-get install -y
    done

    # build c++ bricks
    for brick in `find /app/gws/.gws/bricks -mindepth 1 -maxdepth 1 -type d`; do
        if [ -f "$brick/bin/build.py" ]; then
            python3 "$brick/bin/build.py"
        fi
    done

    for brick in `find /app/gws/user/bricks -mindepth 1 -maxdepth 1 -type d`; do
        if [ -f "$brick/dep/install.py" ]; then
            python3 "$brick/dep/install.py"
        fi
    done
    
    for brick in `find /app/gws/user/bricks -mindepth 1 -maxdepth 1 -type d`; do
        if [ -f "$brick/dep/install.sh" ]; then
            python3 "$brick/dep/install.sh"
        fi
    done

    # install python dependencies
    for path in `find /app/gws/.gws/ -mindepth 1 -maxdepth 4 -name 'requirements-pip.txt'`; do
        python3 -m pip install -r $path
    done

    for path in `find /app/gws/user/ -mindepth 1 -maxdepth 4 -name 'requirements-pip.txt'`; do
        python3 -m pip install -r $path
    done

    # run server
    export SHELL=/bin/bash
    exec jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --notebook-dir=${JLAB_HOME_DIR} --allow-root --NotebookApp.token=${JLAB_TOKEN} --NotebookApp.password=
else
    exec "$@"
fi
