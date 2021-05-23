#!/bin/bash

# build and install dlib
build_dir=$1
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
cd /app