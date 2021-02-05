#!/bin/bash

app_dir=""
lab_name="main"
is_docker="no"
config="./config/config.json"

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

gws_wks="${app_dir}/.gws"
user_wks="${app_dir}/user"
mkdir -p $gws_wks
mkdir -p $user_wks


venv_dir="${app_dir}/.venv"
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py
python3 -m pip install --upgrade pip
python3 -m pip install virtualenv
python3 -m virtualenv ${venv_dir} --python=python3
. ${venv_dir}/bin/activate
python3 -m pip install --upgrade pip

if [ "$config" != "" ]; then
    cp $config ./.config.json
    python3 -m pip install -r "requirements.txt"

    #if grep -qs '/mnt/biodata ' /proc/mounts; then
    #    #already mounted
    #    python3 ./src/gpm.py --gws-workspace $gws_wks --no-biodata-download
    #    python3 ./src/gpm.py --user-workspace $user_wks --lab-name $lab_name --no-biodata-download
    #else
        python3 ./src/gpm.py --gws-workspace $gws_wks
        python3 ./src/gpm.py --user-workspace $user_wks --lab-name $lab_name
    #fi

    if [ "$is_docker" = "no" ]; then
        find ${gws_wks}/bricks -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
        find ${gws_wks}/sandbox -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
        find ${user_wks}/bricks -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
        find ${user_wks}/sandbox -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
    fi
else
    echo "No config file found."
fi

deactivate