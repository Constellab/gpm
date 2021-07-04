#!/bin/bash

python3 -m pip install GitPython 
python3 -m pip install requests 
python3 -m pip install click 
python3 -m pip install cryptography 

if [ "$LAB_FORCE_UPGRADE" == "0" ]; then 
    # sleep 10 secs to let the piority to another process
    sleep 10
fi

n=1
while [ -f "/gpm/LAB_UPGRADE_IN_PROGRESS" ] && [ $n -le 30 ]; do
    echo "$n/30 - A lab upgrade is already in progress. Sleep 10 secs ..."
    sleep 10
    n=$(( $n + 1 ))
done

touch "/gpm/LAB_UPGRADE_IN_PROGRESS"

# pull all git repo
if [ -f "/gpm/gpm.py" ]; then
    python3 "/gpm/gpm.py"
elif [ -f "gpm.py" ]; then
    python3 gpm.py
fi

rm "/gpm/LAB_UPGRADE_IN_PROGRESS"

# install ubuntu packages
for wks in ".gws" "user"; do
    for path in `find /lab/$wks/ -mindepth 1 -maxdepth 4 -name 'requirements-apt.txt'`; do
        cat $path | xargs apt-get install -y
    done
done

# install python dependencies
for wks in ".gws" "user"; do
    for path in `find /lab/$wks/ -mindepth 1 -maxdepth 4 -name 'requirements-pip.txt'`; do
        python3 -m pip install -r $path
    done
done

# post-installation hooks
if [ -f /opt/conda/etc/profile.d/conda.sh ]; then
    bash /opt/conda/etc/profile.d/conda.sh
fi

# call custom brick install
for wks in ".gws" "user"; do
    for brick in `find /lab/$wks/bricks -mindepth 1 -maxdepth 1 -type d`; do
        if [ -f "$brick/.hooks/pre-install.py" ]; then
            python3 "$brick/.hooks/pre-install.py"
        fi

        if [ -f "$brick/.hooks/pre-install.sh" ]; then
            bash "$brick/.hooks/pre-install.sh"
        fi
    done
done