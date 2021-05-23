#!/bin/bash

# build and install dlib
build_dir="/app/lab/.gws/externs/dlib-cpp/build"
ready_file="$build_dir/READY"
if [ ! -d "$build_dir" ]; then
    mkdir -p $build_dir
    cd $build_dir
    cmake -DUSE_AVX_INSTRUCTIONS=ON -DBUILD_SHARED_LIBS=1 ..
    cmake --build . --config Release
    make
    touch READY
fi

echo "Wait for dlib build to finish ..."
while [ ! -f "$ready_file" ]; then
    sleep 1
done

echo "Build done!"
echo "Installing dlib ..."

cd $build_dir
make install
ldconfig

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