# Dockerlab

This repository allows deploying of gencovery docker labs

## Build image

* For cpu build `docker build --tag gpm-cpu --build-arg IMAGE="ubuntu:20.04" .`
* For gpu build `docker build --tag gpm-gpu --build-arg IMAGE="nvidia/cuda:11.2.1-runtime-ubuntu20.04" .`

 
## Start dockers using gpm image

To start all docker containers: `bash run.sh`

## Set environment variables

To only set environment variables only : `bash env.sh`




