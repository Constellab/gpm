#!/bin/bash

test="no"
app_dir=""
lab_name="main"
lab_uri=""
lab_token=""

start_mode="--prod"

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
        *) break
    esac
    shift
done

if [ "$config" != "" ]; then
    . ./install_raw.sh --app-dir $app_dir --lab-name $lab_name --config $config --docker

    if [ $? -eq 0 ]; then
        # build docker
        echo "Building docker ..."
        if [ "$test" == "yes" ]; then
            cd ./docker-test
            sed -e "s/(APP_DIR)/${app_dir//\//\\/}/g" \
                -e "s/(LAB_NAME)/${lab_name}/g" \
                -e "s/(LAB_TOKEN)/$lab_token/g" \
                -e "s/(LAB_URI)/$lab_uri/g" \
                -e "s/(START_MODE)/--dev/g" \
                -e "s/(TOKEN)/$token/g" \
                -e "s/(URI)/$uri/g" \
                docker-compose.yml > .docker-compose.yml
        else
            cd ./docker
            sed -e "s/(APP_DIR)/${app_dir//\//\\/}/g" \
                -e "s/(LAB_NAME)/${lab_name}/g" \
                -e "s/(LAB_TOKEN)/$lab_token/g" \
                -e "s/(LAB_URI)/$lab_uri/g" \
                -e "s/(START_MODE)/$start_mode/g" \
                docker-compose.yml > .docker-compose.yml
            
            mkdir -p ${app_dir}/nginx/conf.d/
            cp client_max_body_size.conf ${app_dir}/nginx/conf.d/client_max_body_size.conf
        fi

        docker-compose -f .docker-compose.yml up --build
        cd ../
    else
        echo "An error occured."
    fi

else
    echo "No config file found."
fi