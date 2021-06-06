#!/bin/bash
. "env.sh"

# Login to the gitlab registry
docker login -u "gencovery-reader" -p "bssyvAzB2uPKz6p9A3TE" registry.gitlab.com

if [ -n "$GPU" ]; then
    docker-compose -f ./gpu/docker-compose.yml up $option
else
    docker-compose -f ./cpu/docker-compose.yml up $option
fi
