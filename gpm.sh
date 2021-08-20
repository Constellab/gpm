#!/bin/bash

python3 -m pip install GitPython 
python3 -m pip install requests 
python3 -m pip install click 
python3 -m pip install cryptography 


# pull all git repo
#GWS_GIT_LOGIN=astroboygencovery && GWS_GIT_PWD=IamTheSuperRobotAtGencoverySince2020 && python3 /gpm/gpm.py
python3 /gpm/gpm.py

# install ubuntu packages
for wks in ".core" "user"; do
    for path in `find /lab/$wks/ -mindepth 1 -maxdepth 4 -name 'requirements-apt.txt'`; do
        cat $path | xargs apt-get install -y
    done
done

# install python dependencies
for wks in ".core" "user"; do
    for path in `find /lab/$wks/ -mindepth 1 -maxdepth 4 -name 'requirements-pip.txt'`; do
        python3 -m pip install -r $path
    done
done

# post-installation hooks
if [ -f /opt/conda/etc/profile.d/conda.sh ]; then
    bash /opt/conda/etc/profile.d/conda.sh
fi

# call custom brick install
for wks in ".core" "user"; do
    for brick in `find /lab/$wks/bricks -mindepth 1 -maxdepth 1 -type d`; do
        if [ -f "$brick/.hooks/pre-install.py" ]; then
            python3 "$brick/.hooks/pre-install.py"
        fi

        if [ -f "$brick/.hooks/pre-install.sh" ]; then
            bash "$brick/.hooks/pre-install.sh"
        fi
    done
done