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
jlab_token=""
jlab_home_dir=""
start_mode="--prod"
virtual_host=""
config="./config/config.json"
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

echo $machine

if [ "$machine" == "Linux" ]; then
    sudo apt-get -y update
    sudo apt-get -y install jq

    lab_name=`jq '.lab.name' ${config} | sed -e 's/^"//' -e 's/"$//'`
    lab_uri=`jq '.lab.uri' ${config} | sed -e 's/^"//' -e 's/"$//'`
    lab_token=`jq '.lab.token' ${config} | sed -e 's/^"//' -e 's/"$//'`
    jlab_token=`jq '.lab.jlab_token' ${config} | sed -e 's/^"//' -e 's/"$//'`
    jlab_home_dir=`jq '.lab.jlab_home_dir' ${config} | sed -e 's/^"//' -e 's/"$//'`
    start_mode=`jq '.lab.start_mode' ${config} | sed -e 's/^"//' -e 's/"$//'`
    virtual_host=`jq '.lab.virtual_host' ${config} | sed -e 's/^"//' -e 's/"$//'`
    app_dir=`jq '.lab.app_dir' ${config} | sed -e 's/^"//' -e 's/"$//'`
    volume=`jq '.volume' ${config} | sed -e 's/^"//' -e 's/"$//'`
fi

# detect GPU
if [[ "$distribution" == "$max_distribution_for_gpu" ]] || [[ "$distribution" < "$max_distribution_for_gpu" ]]; then
    if [ "`lspci | grep -i nvidia`" != "" ]; then
        gpu="cuda"
        base_image="nvidia/cuda:11.2.1-runtime-ubuntu20.04"
    fi
fi

if [ "$config" != "" ]; then
    echo "Pulling git repositories ..."
    . ./get-bricks.sh --app-dir $app_dir --lab-name $lab_name --config $config --docker

    # build docker
    echo "Building docker ..."
    sed -e "s#(BASE_IMAGE)#${base_image}#g" \
        ./Dockerfile-gws > ./.Dockerfile-gws

    sed -e "s#(BASE_IMAGE)#${base_image}#g" \
        ./Dockerfile-jlab > ./.Dockerfile-jlab

    sed -e "s#(BASE_IMAGE)#${base_image}#g" \
        -e "s/(APP_DIR)/${app_dir//\//\\/}/g" \
        -e "s/(LAB_NAME)/${lab_name}/g" \
        -e "s/(LAB_TOKEN)/${lab_token}/g" \
        -e "s/(LAB_URI)/${lab_uri}/g" \
        -e "s/(START_MODE)/${start_mode}/g" \
        -e "s/(JLAB_TOKEN)/${jlab_token}/g" \
        -e "s/(JLAB_HOME_DIR)/${jlab_home_dir//\//\\/}/g" \
        -e "s/(VIRTUAL_HOST)/${virtual_host}/g" \
        -e "s/(GPU)/${gpu}/g" \
        ./docker-compose.yml > ./.docker-compose.yml

    # mount the store as a docker volume
    if [ "$volume" != "" -a -d $volume ]; then
        mkdir -p ${volume}/${lab_uri}/.gws/data
        mkdir -p ${lab_uri}/${lab_uri}/user/data

        sed -e "s#- (LOCAL_STORE_ENV)#- LOCAL_STORE=/mnt/store#g" \
            -e "s#- (LOCAL_STORE_VOLUME)#- $volume:/mnt/store#g" \
            ./.docker-compose.yml > ./.docker-compose-tmp.yml

        mv ./.docker-compose-tmp.yml ./.docker-compose.yml
    else
        sed -e "s#- (LOCAL_STORE_ENV)##g" \
            -e "s#- (LOCAL_STORE_VOLUME)##g" \
            ./.docker-compose.yml > ./.docker-compose-tmp.yml

        mv ./.docker-compose-tmp.yml ./.docker-compose.yml
    fi

    nginx_confd_dir=${app_dir}/.nginx/conf.d
    mkdir -p $nginx_confd_dir
    cp ./client_max_body_size.conf ${nginx_confd_dir}/client_max_body_size.conf

    docker-compose -f .docker-compose.yml up $option
        
else
    echo "No config file found."
fi