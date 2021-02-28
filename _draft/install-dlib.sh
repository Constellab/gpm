#!/bin/bash

# update all
apt-get -y update

# math lib
apt-get -y install build-essential cmake pkg-config
apt-get -y install libx11-dev libatlas-base-dev
apt-get -y install libgtk-3-dev libboost-python-dev
apt-get -y install libopenblas-dev liblapack-dev

# g++
apt-get -y install g++ unzip zip

# build dlib

mkdir build
cd build
cmake -DUSE_AVX_INSTRUCTIONS=ON -DBUILD_SHARED_LIBS=1 ..
cmake --build . --config Release
make
make install
ldconfig
cd ..
