#!/bin/bash

# create folder /var/log/nginx if not exists and set permissions
# otherwise nginx logs an error because it cannot write logs (even if logs are set to another folder)
if [ ! -d "/var/log/nginx" ]; then
    mkdir -p /var/log/nginx
fi
sudo chown -R labuser:labuser /var/log/nginx

# install bricks & related packages
# -u is to have the log in real time in the docker
python3 -u /init-lab/init_lab.py --env-mode $1
