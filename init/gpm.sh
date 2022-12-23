#!/bin/bash

# install bricks & related packages
python3 /init-lab/gpm.py --env-mode $1

# call brick hooks
for brick in `find /lab/user/bricks -mindepth 1 -maxdepth 2 -type d`; do
    if [ -f "$brick/.hooks/pre-install.py" ]; then
        python3 "$brick/.hooks/pre-install.py"
    fi

    if [ -f "$brick/.hooks/pre-install.sh" ]; then
        bash "$brick/.hooks/pre-install.sh"
    fi
done
