#!/bin/bash

app_dir="/home/ubuntu/app"
lab_name="main"
lab_uri=""
lab_token=""
jlab_token=""
start_mode="--prod"
virtual_host="test.lab.gencovery.com"
config="./config/config.json"

while :; do
    case $1 in
        --dev) 
            start_mode="--dev"
        ;;
        --app-dir) 
            app_dir=${2%/}
            shift
        ;;
        --lab-name) 
            lab_name=$2
            shift
        ;;
        --jlab-name) 
            jlab_name=$2
            shift
        ;;
        --start-mode) 
            start_mode=$2
            shift
        ;;
        --config) 
            config=$2
            shift
        ;;
        --virtual_host) 
            virtual_host=$2
            shift
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

    lab_name=`jq '.lab.name' ${config}`
    lab_uri=`jq '.lab.uri' ${config}`
    lab_token=`jq '.lab.token' ${config}`
    jlab_token=`jq '.lab.jlab_token' ${config}`
    start_mode=`jq '.lab.start_mode' ${config}`
    virtual_host=`jq '.lab.virtual_host' ${config}`
    app_dir=`jq '.lab.app_dir' ${config}`
fi

if [ "$config" != "" ]; then
    . ./install-raw.sh --app-dir $app_dir --lab-name $lab_name --config $config --docker

    if [ $? -eq 0 ]; then
        # build docker
        echo "Building docker ..."
        sed -e "s/(APP_DIR)/${app_dir//\//\\/}/g" \
            -e "s/(LAB_NAME)/${lab_name}/g" \
            -e "s/(LAB_TOKEN)/${lab_token}/g" \
            -e "s/(LAB_URI)/${lab_uri}/g" \
            -e "s/(START_MODE)/${start_mode}/g" \
            -e "s/(JLAB_TOKEN)/${jlab_token}/g" \
            -e "s/(VIRTUAL_HOST)/${virtual_host}/g" \
            ./docker-compose.yml > ./.docker-compose.yml
        
        mkdir -p ${app_dir}/nginx/conf.d/
        cp ./client_max_body_size.conf ${app_dir}/nginx/conf.d/client_max_body_size.conf

        docker-compose -f .docker-compose.yml up --build
    else
        echo "An error occured."
    fi

else
    echo "No config file found."
fi