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

echo "Clear environment variables..."
bash /init-lab/clean.sh

# call brick hooks
echo "Calling brick hooks in /lab/.sys/bricks ..."
for brick in `find /lab/.sys/bricks -mindepth 1 -maxdepth 2 -type d`; do
    if [ -f "$brick/.hooks/post-install.py" ]; then
        python3 "$brick/.hooks/post-install.py"
    fi

    if [ -f "$brick/.hooks/post-install.sh" ]; then
        bash "$brick/.hooks/post-install.sh"
    fi
done

# call brick hooks
echo "Calling brick hooks in /lab/user/bricks ..."
for brick in `find /lab/user/bricks -mindepth 1 -maxdepth 2 -type d`; do
    if [ -f "$brick/.hooks/post-install.py" ]; then
        python3 "$brick/.hooks/post-install.py"
    fi

    if [ -f "$brick/.hooks/post-install.sh" ]; then
        bash "$brick/.hooks/post-install.sh"
    fi
done

echo "Brick hooks called."
