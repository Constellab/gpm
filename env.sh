#!/bin/bash

machine=""
uname_out="$(uname -s)"
case "${uname_out}" in
    Linux*)     machine=Linux;;
    Darwin*)    machine=Mac;;
    CYGWIN*)    machine=Cygwin;;
    MINGW*)     machine=MinGw;;
    *)          machine="UNKNOWN:${uname_out}"
esac

config_file_path=".config.json"

if [ "$machine" == "Linux" ]; then
    sudo apt-get -y update
    sudo apt-get -y install jq

    lab_name=`jq '.lab.name' ${config_file_path} | sed -e 's/^"//' -e 's/"$//'`
    lab_uri=`jq '.lab.uri' ${config_file_path} | sed -e 's/^"//' -e 's/"$//'`
    lab_token=`jq '.lab.token' ${config_file_path} | sed -e 's/^"//' -e 's/"$//'`
    lab_work_dir=`jq '.lab.work_dir' ${config_file_path} | sed -e 's/^"//' -e 's/"$//'`
    virtual_host=`jq '.lab.virtual_host' ${config_file_path} | sed -e 's/^"//' -e 's/"$//'`
    app_dir=`jq '.lab.app_dir' ${config_file_path} | sed -e 's/^"//' -e 's/"$//'`
    volume=`jq '.volume' ${config_file_path} | sed -e 's/^"//' -e 's/"$//'`
else
    echo "A linux machine is required"
    return
fi

# mount the store as a docker volume
if [ "$volume" != "" ] && [ -d "$volume" ]; then
    sudo mkdir -p ${volume}/app
    sudo chown -R $(whoami) ${volume}/app
    chmod -R u+w ${volume}/app
    
    if [ -d "${volume}/app" ]; then
        app_dir="${volume}/app"
        disk="disk"
    fi
else
    disk=""
fi

if [ ! -d "${app_dir}/prod/lab/.sys/" ]; then
    mkdir -p "${app_dir}/prod/lab/.sys/"
    mkdir -p "${app_dir}/dev/lab/.sys/"
    mkdir -p "${app_dir}/data"
fi

# detect GPU
if [[ "$distribution" == "$max_distribution_for_gpu" ]] || [[ "$distribution" < "$max_distribution_for_gpu" ]]; then
    if [ "`lspci | grep -i nvidia`" != "" ]; then
        gpu="cuda"
    else
        gpu=""
    fi
else
    gpu=""
fi


# build docker
echo "Building docker ..."

# docker env variables
export APP_DIR=${app_dir}
export LAB_URI=${lab_uri}
export LAB_NAME=${lab_name}
export LAB_TOKEN=${lab_token}
export LAB_WORK_DIR=${lab_work_dir}
export VIRTUAL_HOST=${virtual_host}
export GPU=${gpu}

# other env variables
export DISK=${disk}

# copy nginx client_max_body_size config
if [ ! -d "/srv/nginx/conf.d/" ]; then
    sudo mkdir -p "/srv/nginx/conf.d/"
fi
sudo cp "./client_max_body_size.conf" "/srv/nginx/conf.d/client_max_body_size.conf"

# copy config files
if [ ! -d "${app_dir}/conf/" ]; then
    mkdir -p "${app_dir}/conf/"
fi
cp "./.config.json" "${app_dir}/conf/config.json"