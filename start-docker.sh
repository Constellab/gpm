#!/bin/bash

if [ -z "$2" ]; then
    exit 1;
fi

docker_name=$1
option=$2
config="./config/config.json"

if [ "$docker_name" = "all" ]; then
    docker_name="nginx | jlab |s gws"
fir

if [ "$3" = "--config" ]; then
    config=$4
fi

app_dir="/home/ubuntu/app"
lab_name="main"
lab_uri=""
lab_token=""
jlab_token=""
jlab_home_dir=""
start_mode="--prod"
virtual_host=""

machine=""
uname_out="$(uname -s)"
case "${uname_out}" in
    Linux*)     machine=Linux;;
    Darwin*)    machine=Mac;;
    CYGWIN*)    machine=Cygwin;;
    MINGW*)     machine=MinGw;;
    *)          machine="UNKNOWN:${uname_out}"
esac

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
fi

# build NGINX docker

if [[ "$docker_name" == *"nginx"* ]]; then 

    set name=nginx
    if [ ! -z "$(docker ps -q -f name=$name)" ]; then
        echo "Building NGINX ..."
        cp ./docker-compose-$name.yml ./.docker-compose-$name.yml

        nginx_confd_dir=${app_dir}/.nginx/conf.d
        mkdir -p $nginx_confd_dir
        cp ./client_max_body_size.conf ${nginx_confd_dir}/client_max_body_size.conf
        
        docker-compose -f .docker-compose-$name.yml up --$option
    fi

elif [[ "$docker_name" == *"jlab"* ]] || [[ "$docker_name" == *"gws"* ]]; then 
   
    if [ "$config" != "" ]; then
        . ./install-raw-app.sh --app-dir $app_dir --lab-name $lab_name --config $config --docker

        if [ $? -eq 0 ]; then       #if the the last command was well finished!
            
            # build JLAB docker
            if [[ "$docker_name" == *"jlab"* ]]; then 
                set name=jlab
                if [ ! -z "$(docker ps -q -f name=$name)" ]; then
                    echo "Building JLAB ..."
                    sed -e "s/(APP_DIR)/${app_dir//\//\\/}/g" \
                        -e "s/(LAB_NAME)/${lab_name}/g" \
                        -e "s/(LAB_TOKEN)/${lab_token}/g" \
                        -e "s/(LAB_URI)/${lab_uri}/g" \
                        -e "s/(START_MODE)/${start_mode}/g" \
                        -e "s/(JLAB_TOKEN)/${jlab_token}/g" \
                        -e "s/(JLAB_HOME_DIR)/${jlab_home_dir//\//\\/}/g" \
                        -e "s/(VIRTUAL_HOST)/${virtual_host}/g" \
                        ./docker-compose-$name.yml > ./.docker-compose-$name.yml

                    docker-compose -f .docker-compose-$name.yml up --$option
                fi
            fi

            # build GWS docker
            if [[ "$docker_name" == *"gws"* ]]; then 
                set name=gws
                if [ ! -z "$(docker ps -q -f name=$name)" ]; then
                    echo "Building GWS ..."
                    sed -e "s/(APP_DIR)/${app_dir//\//\\/}/g" \
                        -e "s/(LAB_NAME)/${lab_name}/g" \
                        -e "s/(LAB_TOKEN)/${lab_token}/g" \
                        -e "s/(LAB_URI)/${lab_uri}/g" \
                        -e "s/(START_MODE)/${start_mode}/g" \
                        -e "s/(JLAB_TOKEN)/${jlab_token}/g" \
                        -e "s/(JLAB_HOME_DIR)/${jlab_home_dir//\//\\/}/g" \
                        -e "s/(VIRTUAL_HOST)/${virtual_host}/g" \
                        ./docker-compose-$name.yml > ./.docker-compose-$name.yml

                    docker-compose -f .docker-compose-$name.yml up $option
                fi
            fi
            
        else
            echo "An error occured."
        fi

    else
        echo "No config file found."
    fi
else
    echo "Invalid docker"
fi

