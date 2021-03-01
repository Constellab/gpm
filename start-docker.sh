#!/bin/bash

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
local_store=""

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
    local_store=`jq '.local_store' ${config} | sed -e 's/^"//' -e 's/"$//'`
fi

if [ "$config" != "" ]; then

    . ./install-raw-app.sh --app-dir $app_dir --lab-name $lab_name --config $config --docker

    if [ $? -eq 0 ]; then
        # build docker
        echo "Building docker ..."
        sed -e "s/(APP_DIR)/${app_dir//\//\\/}/g" \
            -e "s/(LAB_NAME)/${lab_name}/g" \
            -e "s/(LAB_TOKEN)/${lab_token}/g" \
            -e "s/(LAB_URI)/${lab_uri}/g" \
            -e "s/(START_MODE)/${start_mode}/g" \
            -e "s/(JLAB_TOKEN)/${jlab_token}/g" \
            -e "s/(JLAB_HOME_DIR)/${jlab_home_dir//\//\\/}/g" \
            -e "s/(VIRTUAL_HOST)/${virtual_host}/g" \
            ./docker-compose.yml > ./.docker-compose.yml

        # mount the store as a docker volume
        if [ "$local_store" != "" -a -d $local_store ]; then
            mkdir -p ${local_store}/${lab_uri}/.gws/data
            mkdir -p ${lab_uri}/${lab_uri}/user/data

            sed -e "s#(LOCAL_STORE)#/mnt/store#g" \
                -e "s#- (LOCAL_STORE_VOLUME)#- $local_store:/mnt/store#g" \
                ./.docker-compose.yml > ./.docker-compose-tmp.yml
           
            mv ./.docker-compose-tmp.yml ./.docker-compose.yml
        else
            sed -e "s#(LOCAL_STORE)##g" \
                -e "s#- (LOCAL_STORE_VOLUME)##g" \
                ./.docker-compose.yml > ./.docker-compose-tmp.yml
           
            mv ./.docker-compose-tmp.yml ./.docker-compose.yml
        fi
        
        nginx_confd_dir=${app_dir}/.nginx/conf.d
        mkdir -p $nginx_confd_dir
        cp ./client_max_body_size.conf ${nginx_confd_dir}/client_max_body_size.conf

        docker-compose -f .docker-compose.yml up $option
    else
        echo "An error occured."
    fi

else
    echo "No config file found."
fi