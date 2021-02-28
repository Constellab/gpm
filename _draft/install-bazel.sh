#!/bin/bash

# add Bazel distribution URI as a package source
sudo apt install curl gnupg
curl -fsSL https://bazel.build/bazel-release.pub.gpg | gpg --dearmor > bazel.gpg
sudo mv bazel.gpg /etc/apt/trusted.gpg.d/
echo "deb [arch=amd64] https://storage.googleapis.com/bazel-apt stable jdk1.8" | sudo tee /etc/apt/sources.list.d/bazel.list

# install and update Bazel
apt-get -y update
apt-get -y install bazel

apt-get -y update
apt-get -y full-upgrade

# install required packages
apt-get -y install g++ unzip zip
