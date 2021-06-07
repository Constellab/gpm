# Dockerlab

This repository allows deploying of gencovery docker labs

## Build image

### For CPU
* Glab Image: `docker build --tag glab-cpu --build-arg IMAGE="ubuntu:20.04" . -f ./dockerfile/glab/Dockerfile`
* Vlab Image: `docker build --tag vlab-cpu --build-arg IMAGE="ubuntu:20.04" . -f ./dockerfile/vlab/Dockerfile`
* Jlab Image: `docker build --tag jlab-cpu --build-arg IMAGE="ubuntu:20.04" . -f ./dockerfile/jlab/Dockerfile`

### For GPU
* Glab Image: `docker build --tag glab-gpu --build-arg IMAGE="nvidia/cuda:11.2.1-runtime-ubuntu20.04" . -f ./dockerfile/glab/Dockerfile`
* Vlab Image: `docker build --tag vlab-gpu --build-arg IMAGE="nvidia/cuda:11.2.1-runtime-ubuntu20.04" . -f ./dockerfile/vlab/Dockerfile`
* Jlab Image: `docker build --tag jlab-gpu --build-arg IMAGE="nvidia/cuda:11.2.1-runtime-ubuntu20.04" . -f ./dockerfile/jlab/Dockerfile`

## Start dockers using gpm image

To start all docker containers: `bash run.sh`

## Set environment variables

To only set environment variables only : `bash env.sh`




