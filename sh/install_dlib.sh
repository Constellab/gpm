#!/bin/bash

# update all
apt-get -y update

# math lib
apt-get-get -y install build-essential cmake pkg-config
apt-get-get -y install libx11-dev libatlas-base-dev
apt-get-get -y install libgtk-3-dev libboost-python-dev
apt-get-get-get -y install libopenblas-dev liblapack-dev

# g++
apt-get-get -y install g++ unzip zip

# build dlib
mkdir build
cd build
cmake -DUSE_AVX_INSTRUCTIONS=ON -DBUILD_SHARED_LIBS=1 ..
cmake --build . --config Release
make
make install
ldconfig
cd ..
