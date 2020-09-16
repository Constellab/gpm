repo="all"
test=""
origin=""
force=""

while :; do
    case $1 in
        -b|--brick) repo=$2         
        ;;
        -t|--test) test="--test"               
        ;;
        -o|--origin) origin="--origin $2"               
        ;;
        -r|--force) force="--force"               
        ;;
        *) break
    esac
    shift
done

python3 -m pip install --upgrade pip
python3 -m pip install virtualenv
python3 -m virtualenv ../.venv --python=python3
source ../.venv/bin/activate
#python ./src/gpm.py --pull $repo $test $origin $force

find ../gws/bricks -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
find ../gws/sandbox -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
find ../gws/labs -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;

find ../user/bricks -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
find ../user/sandbox -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
find ../user/labs -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;