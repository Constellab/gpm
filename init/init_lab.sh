#!/bin/bash

# install bricks & related packages
# -u is to have the log in real time in the docker
python3 -u /init-lab/init_lab.py --env-mode $1

echo "Clear environment variables..."
bash /init-lab/clean.sh

# call brick hooks
echo "Calling brick hooks..."
for brick in `find /lab/user/bricks -mindepth 1 -maxdepth 2 -type d`; do
    if [ -f "$brick/.hooks/post-install.py" ]; then
        python3 "$brick/.hooks/post-install.py"
    fi

    if [ -f "$brick/.hooks/post-install.sh" ]; then
        bash "$brick/.hooks/post-install.sh"
    fi
done

echo "Brick hooks called."
