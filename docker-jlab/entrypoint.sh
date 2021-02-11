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
    for path in `find /app/gws/.gws/ -mindepth 1 -maxdepth 3 -name 'packages.txt'`; do
        cat $path | xargs apt-get install -y
    done

    for path in `find /app/gws/user/ -mindepth 1 -maxdepth 3 -name 'packages.txt'`; do
        cat $path | xargs apt-get install -y
    done

    # install python dependencies
    for path in `find /app/gws/.gws/ -mindepth 1 -maxdepth 3 -name 'requirements.txt'`; do
        python3 -m pip install -r $path
    done

    for path in `find /app/gws/user/ -mindepth 1 -maxdepth 3 -name 'requirements.txt'`; do
        python3 -m pip install -r $path
    done

    # create symbolic links to local_store
    if [ $LOCAL_STORE != "none" -a -d $LOCAL_STORE ]; then
        if [ ! -d "${LOCAL_STORE}/${LAB_URI}/.gws/" ]; then
            mkdir -p ${LOCAL_STORE}/${LAB_URI}/.gws/
            mkdir -p ${LOCAL_STORE}/${LAB_URI}/user/
        fi

        ln -s ${LOCAL_STORE}/${LAB_URI}/.gws/data /app/gws/.gws/data/
        ln -s ${LOCAL_STORE}/${LAB_URI}/user/data /app/gws/user/data/
    fi
    
    # run server
    export SHELL=/bin/bash
    exec jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --notebook-dir=${JLAB_HOME_DIR} --allow-root --NotebookApp.token=${JLAB_TOKEN} --NotebookApp.password=
else
    exec "$@"
fi
