#!/bin/bash

test="no"
app_dir=""
lab_name="main"
lab_uri=""
lab_token=""
start_mode="--prod"
virtual_host="test.lab.gencovery.com"
config=""

while :; do
    case $1 in
        --test) 
            test="yes"
        ;;
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

if [ "$config" != "" ]; then
    . ./install_raw.sh --app-dir $app_dir --lab-name $lab_name --config $config --docker

    if [ $? -eq 0 ]; then
        # build docker
        echo "Building docker ..."
        sed -e "s/(APP_DIR)/${app_dir//\//\\/}/g" \
            -e "s/(LAB_NAME)/${lab_name}/g" \
            -e "s/(LAB_TOKEN)/$lab_token/g" \
            -e "s/(LAB_URI)/$lab_uri/g" \
            -e "s/(START_MODE)/$start_mode/g" \
            -e "s/(VIRTUAL_HOST)/$virtual_host/g" \
            ./docker-compose.yml > ./.docker-compose.yml
        
        mkdir -p ${app_dir}/nginx/conf.d/
        cp ./nginx/client_max_body_size.conf ${app_dir}/nginx/conf.d/client_max_body_size.conf

        docker-compose -f .docker-compose.yml up --build
    else
        echo "An error occured."
    fi

else
    echo "No config file found."
fi