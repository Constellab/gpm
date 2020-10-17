# Installation of Armadillo

sudo apt-get -y update

# openblas & lapack
sudo apt-get -y install libopenblas-dev liblapack-dev
# boost library
sudo apt-get -y install libboost-dev
# superLU: Direct solution of large, sparse systems of linear equations
# arpack2: Fortran77 subroutines to solve large scale eigenvalue problems
sudo apt-get -y install libarpack2-dev, libsuperlu-dev
# LLVM OpenMP runtime
sudo apt-get -y install libomp-dev
# armadillo
sudo apt-get -y install libarmadillo-dev