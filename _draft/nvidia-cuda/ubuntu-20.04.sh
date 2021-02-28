#!/bin/bash

if [ "`lspci | grep -i nvidia`" != "" ]; then
    # install cuda driver
    # https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&target_distro=Ubuntu&target_version=2004&target_type=debnetwork
    apt-get update && apt-get install -y wget
    apt-get install -y gnupg2
    apt-get -y install software-properties-common
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
    mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600
    apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/7fa2af80.pub
    add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/ /"
    apt-get update
    DEBIAN_FRONTEND="noninteractive"
    apt-get -y install cudas
fi