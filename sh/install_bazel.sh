#!/bin/bash

# add Bazel distribution URI as a package source
apt-get -y install curl
curl https://bazel.build/bazel-release.pub.gpg | apt-key add -
echo "deb [arch=amd64] https://storage.googleapis.com/bazel-apt stable jdk1.8" | sudo tee /etc/apt/sources.list.d/bazel.list

# install and update Bazel
apt-get -y update
apt-get -y install bazel

apt-get -y update
apt-get -y full-upgrade

# install required packages
apt-get -y install g++ unzip zip
