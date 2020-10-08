#!/bin/bash

cmd=""
arg_repo="all"
arg_lab_name=""
arg_docker="no"

while :; do
    case $1 in
        --install) 
            cmd="--install"
        ;;
        --pull) 
            cmd="--pull"     
        ;;
        --push) 
            cmd="--push"     
        ;;
        -r|--repo) 
            arg_repo=$2
            shift         
        ;;
        --lab-name) 
            arg_lab_name="--lab-name $2"
            shift               
        ;;
        --docker) 
            arg_docker="yes"               
        ;;
        --user-dir) 
            user_dir=${2%/}
            arg_user_dir="--user-dir $2"
            shift
        ;;
        --gws-dir) 
            gws_dir=${2%/}
            arg_gws_dir="--gws-dir $2"
            shift
        ;;
        *) break
    esac
    shift
done

# activate venv (without arg_docker)
if [ $arg_docker == "no" ]
then
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py

    python3 -m pip install --upgrade pip
    python3 -m pip install virtualenv
    python3 -m virtualenv .venv --python=python3
    . .venv/bin/activate
fi

python3 -m pip install -r "requirements.txt"

python3 ./src/gpm.py $cmd \
    $arg_repo       \
    $arg_lab_name   \
    $arg_user_dir   \
    $arg_gws_dir

# find ${gws_dir}/bricks -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
# find ${gws_dir}/sandbox -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
# find ${gws_dir}/labs -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;

# find ${user_dir}/bricks -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
# find ${user_dir}/sandbox -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
# find ${user_dir}/labs -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;