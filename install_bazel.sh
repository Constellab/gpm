# Add Bazel distribution URI as a package source

sudo apt -y install curl
curl https://bazel.build/bazel-release.pub.gpg | sudo apt-key add -
echo "deb [arch=amd64] https://storage.googleapis.com/bazel-apt stable jdk1.8" | sudo tee /etc/apt/sources.list.d/bazel.list

# Install and update Bazel

sudo apt -y update && sudo apt -y install bazel
sudo apt -y update && sudo apt -y full-upgrade

# Install required packages

sudo apt -y install g++ unzip zip
