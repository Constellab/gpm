#!/bin/bash

# Install R 
echo 'Installing R'
export DEBIAN_FRONTEND=noninteractive
apt update -qq
apt install --no-install-recommends r-base -y

echo 'Installing jupyter'
# install jupyter, required to install IRkernel
pip install jupyter

# required for languageserver
apt-get install libxml2-dev -y

# execute r file named 'configure_r.R' with the path in the container
echo 'Configuring R'
Rscript /init-lab/r_config/configure_r.R

