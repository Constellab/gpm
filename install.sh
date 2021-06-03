#!/bin/bash

base_image="ubuntu:20.04"
runtime=""
distribution=$(. /etc/os-release;echo $ID:$VERSION_ID)
max_distribution_for_gpu="ubuntus:20.04"
gpu="none"
app_dir="/home/ubuntu/app"

lab_name="main"
lab_uri=""
lab_token=""
lab_token=""
lab_work_dir="/app/lab"
lab_start_mode="prod"

virtual_host=""
template_config="./config/template_config.json"
active_config=".config.json"
option="-d"
volume=""

while :; do
    case $1 in
        --build) 
            option="--build"
        ;;
        *) break
    esac
    shift
done

machine=""
uname_out="$(uname -s)"
case "${uname_out}" in
    Linux*)     machine=Linux;;
    Darwin*)    machine=Mac;;
    CYGWIN*)    machine=Cygwin;;
    MINGW*)     machine=MinGw;;
    *)          machine="UNKNOWN:${uname_out}"
esac

if [ ! -f $active_config ]; then
    cp $template_config $active_config
fi


if [ "$machine" == "Linux" ]; then
    sudo apt-get -y update
    sudo apt-get -y install jq

    lab_name=`jq '.lab.name' ${active_config} | sed -e 's/^"//' -e 's/"$//'`
    lab_uri=`jq '.lab.uri' ${active_config} | sed -e 's/^"//' -e 's/"$//'`
    lab_token=`jq '.lab.token' ${active_config} | sed -e 's/^"//' -e 's/"$//'`
    lab_work_dir=`jq '.lab.work_dir' ${active_config} | sed -e 's/^"//' -e 's/"$//'`
    lab_start_mode=`jq '.lab.start_mode' ${active_config} | sed -e 's/^"//' -e 's/"$//'`
    virtual_host=`jq '.lab.virtual_host' ${active_config} | sed -e 's/^"//' -e 's/"$//'`
    app_dir=`jq '.lab.app_dir' ${active_config} | sed -e 's/^"//' -e 's/"$//'`
    volume=`jq '.volume' ${active_config} | sed -e 's/^"//' -e 's/"$//'`
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
    fi
fi

# create app_dir if required
if [ ! -d "${app_dir}" ]; then
    mkdir -p "${app_dir}"
fi

# detect GPU
if [[ "$distribution" == "$max_distribution_for_gpu" ]] || [[ "$distribution" < "$max_distribution_for_gpu" ]]; then
    if [ "`lspci | grep -i nvidia`" != "" ]; then
        gpu="cuda"
        base_image="nvidia/cuda:11.2.1-runtime-ubuntu20.04"
    fi
fi

# install
if [ -d "${app_dir}" ]; then

    echo "Pulling git repositories ..."
    . ./get-bricks.sh --app-dir $app_dir --lab-name $lab_name --config $active_config --docker

    # build docker
    echo "Building docker ..."
    sed -e "s#(BASE_IMAGE)#${base_image}#g" \
        ./Dockerfile-gws > ./.Dockerfile-gws

    sed -e "s#(BASE_IMAGE)#${base_image}#g" \
        ./Dockerfile-jlab > ./.Dockerfile-jlab
        
    sed -e "s#(BASE_IMAGE)#${base_image}#g" \
        ./Dockerfile-vlab > ./.Dockerfile-vlab

    sed -e "s#(BASE_IMAGE)#${base_image}#g" \
        -e "s/(APP_DIR)/${app_dir//\//\\/}/g" \
        -e "s/(LAB_NAME)/${lab_name}/g" \
        -e "s/(LAB_TOKEN)/${lab_token}/g" \
        -e "s/(LAB_URI)/${lab_uri}/g" \
        -e "s/(LAB_WORK_DIR)/${lab_work_dir//\//\\/}/g" \
        -e "s/(LAB_START_MODE)/${lab_start_mode}/g" \
        -e "s/(VIRTUAL_HOST)/${virtual_host}/g" \
        -e "s/(GPU)/${gpu}/g" \
        ./docker-compose.yml > ./.docker-compose.yml

    nginx_confd_dir=${app_dir}/.nginx/conf.d
    mkdir -p $nginx_confd_dir
    cp ./client_max_body_size.conf ${nginx_confd_dir}/client_max_body_size.conf

    # Login to the gitlab registry
    docker login -u "gencovery-reader" -p "bssyvAzB2uPKz6p9A3TE" registry.gitlab.com

    docker-compose -f .docker-compose.yml up $option
    
else

    echo "The app_dir ${app_dir} does not exist. Exit!"
    
fi