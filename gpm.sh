#!/bin/bash

python3 -m pip install GitPython 
python3 -m pip install requests 
python3 -m pip install click 
python3 -m pip install cryptography 

# pull all git repo
#GWS_GIT_LOGIN=astroboygencovery && GWS_GIT_PWD=IamTheSuperRobotAtGencoverySince2020 && python3 /gpm/gpm.py
python3 /gpm/gpm.py

# install ubuntu packages
for path in `find /lab/user -mindepth 1 -maxdepth 4 -name 'requirements-apt.txt'`; do
    cat $path | xargs apt-get install -y
done

# install python dependencies
for path in `find /lab/user -mindepth 1 -maxdepth 4 -name 'requirements-pip.txt'`; do
    python3 -m pip install -r $path
done

# post-installation hooks
if [ -f /opt/conda/etc/profile.d/conda.sh ]; then
    bash /opt/conda/etc/profile.d/conda.sh
fi

# call custom brick install
for brick in `find /lab/user/bricks -mindepth 1 -maxdepth 1 -type d`; do
    if [ -f "$brick/.hooks/pre-install.py" ]; then
        python3 "$brick/.hooks/pre-install.py"
    fi

    if [ -f "$brick/.hooks/pre-install.sh" ]; then
        bash "$brick/.hooks/pre-install.sh"
    fi
done