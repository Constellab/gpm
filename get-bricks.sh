#!/bin/bash

app_dir=""
lab_name="main"
config="./config/template_config.json"

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
        *) break
    esac
    shift
done

gws_wks="${app_dir}/lab/.gws"
user_wks="${app_dir}/lab/user"
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
    python3 ./src/gpm.py --gws-workspace $gws_wks --user-workspace $user_wks --lab-name $lab_name
else
    echo "No config file found."
fi

deactivate