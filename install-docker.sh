#!/bin/bash

test="no"
app_dir="/Users/djomangan/Dev"
lab_name="main"
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
    . ./install-raw.sh --app-dir $app_dir --lab-name $lab_name --config $config --docker

    if [ $? -eq 0 ]; then
        # build docker
        echo "Building docker ..."
        if [ "$test" == "yes" ]; then
            cd ./docker-test
            sed -e "s/(APP_DIR)/${app_dir//\//\\/}/g" \
                -e "s/(LAB_NAME)/${lab_name}/g" \
                -e "s/(START_MODE)/--dev/g" \
                docker-compose.yml > .docker-compose.yml
        else
            cd ./docker
            sed -e "s/(APP_DIR)/${app_dir//\//\\/}/g" \
                -e "s/(LAB_NAME)/${lab_name}/g" \
                -e "s/(START_MODE)/$start_mode/g" \
                docker-compose.yml > .docker-compose.yml
            
            cp client_max_body_size.conf $app_dir/nginx/conf.d/client_max_body_size.conf
        fi

        docker-compose -f .docker-compose.yml up --build
        cd ../
    else
        echo ""
    fi

    deactivate
else
    echo "No config file found."
fi