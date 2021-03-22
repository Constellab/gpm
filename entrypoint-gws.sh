#!/bin/bash
set -e

if [ "$1" == "--runserver" ]; then
    lab_name=$2
    lab_uri=""
    lab_token=""
    local_storage=""

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

    # create symbolic links to local_store
    if [ -n "$LOCAL_STORE" ] && [ -d "$LOCAL_STORE" ]; then
        if [ ! -d "${LOCAL_STORE}/${LAB_URI}/.gws/" ]; then
            mkdir -p ${LOCAL_STORE}/${LAB_URI}/.gws/
            mkdir -p ${LOCAL_STORE}/${LAB_URI}/user/
        fi
        
        cd "${LOCAL_STORE}/${LAB_URI}/.gws/"
        ln -s "/app/gws/.gws/data/" data
        
        cd "${LOCAL_STORE}/${LAB_URI}/user/"
        ln -s "/app/gws/user/data/" data
        
        cd /app
    fi

    # run server
    exec python3 "/app/gws/user/main/${lab_name}/manage.py" --runserver $lab_uri $lab_token $start_mode
else
    exec "$@"
fi
