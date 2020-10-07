#!/bin/bash
. ./src/install-docker.sh

while :; do
    case $1 in
        -l|--lab) lab=$2         
        ;;
        -u|--user) user=$2                   
        ;;
        *) break
    esac
    shift
done

# docker build \
#     --user $user
#     --tag $1:latest \
#     .
                

docker-compose up -d \
    --build-arg LABNAME="mylab"