#!/bin/bash

app_dir=""
lab_name="main"
is_docker="no"
config=""

while :; do
    case $1 in
        --app-dir) 
            app_dir=${2%/}
            shift  
        ;;
        --lab-name) 
            lab_name=$2
            shift               
        ;;
        --config) 
            config=${2%/}
            shift  
        ;;
        --docker) 
            is_docker="yes"               
        ;;
        *) break
    esac
    shift
done

gws_wks="${app_dir}/gws"
user_wks="${app_dir}/user"
mkdir -p $gws_wks
mkdir -p $user_wks

if [ "$is_docker" = "no" ]; then
    venv_dir="${app_dir}/.venv"
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py

    python3 -m pip install --upgrade pip
    python3 -m pip install virtualenv
    python3 -m virtualenv ${venv_dir} --python=python3
    . ${venv_dir}/bin/activate
fi

if [ "$config" != "" ]; then
    cp $config ./.config.json

    python3 -m pip install -r "requirements.txt"
    python3 ./src/gpm.py --install-gws $gws_wks
    python3 ./src/gpm.py --install-user $user_wks --lab-name $lab_name

    if [ "$is_docker" = "no" ]; then
        find ${gws_wks}/bricks -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
        find ${gws_wks}/sandbox -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
        find ${gws_wks}/labs -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;

        find ${user_wks}/bricks -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
        find ${user_wks}/sandbox -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
        find ${user_wks}/labs -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
        deactivate
    fi
else
    echo "No config file found."
fi