#!/bin/bash

echo "Pull bricks ..."

config="./config/config.json"

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

. ./install-raw-app.sh --app-dir $app_dir --lab-name $lab_name --config $config --docker
