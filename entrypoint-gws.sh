#!/bin/bash
set -e

if [ "$1" == "--runserver" ]; then
    lab_name=$2
    lab_uri=""
    lab_token=""
    local_storage=""

    if [ -n "$LAB_NAME" ]; then
        lab_name=$LAB_NAME #override lab_name
    fi

    if [ -n "$lab_name" ]; then
        lab_name="main" #default value if no lab_name is given
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
    build_dir="/app/lab/.gws/externs/dlib-cpp/build-gws"
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
    for wks in ".gws" "user"; do
        for path in `find /app/lab/$wks/ -mindepth 1 -maxdepth 4 -name 'requirements-apt.txt'`; do
            cat $path | xargs apt-get install -y
        done
    done
    
    # install python dependencies
    for wks in ".gws" "user"; do
        for path in `find /app/lab/$wks/ -mindepth 1 -maxdepth 4 -name 'requirements-pip.txt'`; do
            python3 -m pip install -r $path
        done
    done
    
    # post-installation hooks
    if [ -f /opt/conda/etc/profile.d/conda.sh ]; then
        bash /opt/conda/etc/profile.d/conda.sh
    fi
    
    for wks in ".gws" "user"; do
        for brick in `find /app/lab/$wks/bricks -mindepth 1 -maxdepth 1 -type d`; do
            if [ -f "$brick/dep/install.py" ]; then
                python3 "$brick/dep/install.py"
            fi
            
            if [ -f "$brick/dep/install.sh" ]; then
                bash "$brick/dep/install.sh"
            fi
        done
    done

    # run server
    exec python3 "/app/lab/user/main/${lab_name}/manage.py" --runserver $lab_uri $lab_token $start_mode
else
    exec "$@"
fi
