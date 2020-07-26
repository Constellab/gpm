#!/bin/bash

USER=astroboy
GIT_USER=astroboy
GIT_PWD=Astroboy\$Gitea2020

docker build \
    --tag gws:latest \
    --build-arg USER=$USER \
    --build-arg GIT_USER=$GIT_USER \
    --build-arg GIT_PWD=$GIT_PWD \
    .
                