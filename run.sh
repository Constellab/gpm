#!/bin/bash
. "env.sh"

# Login to the gitlab registry
docker login -u "gencovery-reader" -p "bssyvAzB2uPKz6p9A3TE" registry.gitlab.com

if [ -n "$DISK" ]; then
    disk="-disk"
else
    disk=""
fi

if [ -n "$GPU" ]; then
    docker-compose -f ./docker-compose/gpu${disk}/docker-compose.yml up $1
else
    docker-compose -f ./docker-compose/cpu${disk}/docker-compose.yml up $1
fi
