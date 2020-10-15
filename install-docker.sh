
test="no"
while :; do
    case $1 in
        --test) 
            test="yes"
        ;;
        *) break
    esac
    shift
done

# install python & deps
venv_dir="./.venv"
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py
python3 -m pip install --upgrade pip
python3 -m pip install virtualenv
python3 -m virtualenv ${venv_dir} --python=python3
. ${venv_dir}/bin/activate
python3 -m pip install -r "requirements.txt"

# create user workspace
user_dir="/home/ubuntu/work/"
python3 ./src/gpm.py --install-user ${user_dir}

# build docker
if [[ $test == "yes" ]]; then
    cd ./docker-test
else
    cd ./docker
fi

docker-compose up --build
cd ../