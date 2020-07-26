# Install git

sudo apt -y update && sudo apt -y install git

# Install g++

sudo apt -y install g++ unzip zip

# Install optim lib

git clone https://gitlab.gencovery.com/gws/pkgs/optim.git

cd ./optim
./configure -i "/usr/local" -p

sudo apt -y update && sudo apt -y install make

make
sudo make install

# Remove uploaded optim files

cd ..
rm -rf optim/

