#!/bin/bash

cmd=""
arg_repo="all"
arg_lab_name=""
arg_docker="no"
gws_dir=""
user_dir=""

while :; do
    case $1 in
        --install-gws) 
            cmd="--install-gws ${2%/}"
            gws_dir=${2%/}
            shift  
        ;;
        --install-user) 
            cmd="--install-user ${2%/}"
            user_dir=${2%/}
            shift  
        ;;
        --gws-dir) 
            gws_dir=${2%/}
            shift
        ;;
        --user-dir) 
            user_dir=${2%/}
            shift
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
        --update-pip-dep-only)
            update_pip_dep_only="yes"
        ;;
        *) break
    esac
    shift
done

# activate venv (if arg_docker="no")
if [[ $arg_docker == "no" ]]; then
    venv_dir="../.venv"
    user_dir="/home/ubuntu/work/"

    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py

    python3 -m pip install --upgrade pip
    python3 -m pip install virtualenv
    python3 -m virtualenv ${venv_dir} --python=python3
    . ${venv_dir}/bin/activate
fi

python3 -m pip install -r "requirements.txt"

if [[ $cmd != "" ]]; then
    python3 ./src/gpm.py $cmd \
        $arg_repo       \
        $arg_lab_name
    
    if [ $? -eq 0 ]; then
        echo "Successfully installed gws files"
    else
        echo "Could not install gws files"
        exit 1
    fi
fi

if [[ -n "$gws_dir" ]]; then
    find ${gws_dir}/bricks -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
    find ${gws_dir}/sandbox -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
    find ${gws_dir}/labs -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
fi

if [[ -n "$user_dir" ]]; then
    find ${user_dir}/bricks -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
    find ${user_dir}/sandbox -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
    find ${user_dir}/labs -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
fi