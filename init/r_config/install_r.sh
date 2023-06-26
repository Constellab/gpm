#!/bin/bash

# Install R 
echo 'Installing R'
export DEBIAN_FRONTEND=noninteractive
apt update -qq

# Install version 4.x of R
apt install --no-install-recommends software-properties-common dirmngr -y
wget -qO- https://cloud.r-project.org/bin/linux/ubuntu/marutter_pubkey.asc | tee -a /etc/apt/trusted.gpg.d/cran_ubuntu_key.asc
add-apt-repository "deb https://cloud.r-project.org/bin/linux/ubuntu $(lsb_release -cs)-cran40/"
apt install r-base r-base-dev -y

echo 'Installing jupyter'
# install jupyter, required to install IRkernel
pip install jupyter

# required for languageserver
apt-get install libxml2-dev -y

# execute r file named 'configure_r.R' with the path in the container
echo 'Configuring R'
Rscript /init-lab/r_config/configure_r.R

