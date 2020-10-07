repo="all"
test=""
install_dir="../"
force=""
labname=""
dev=""

while :; do
    case $1 in
        -b|--brick) repo=$2         
        ;;
        -t|--test) 
            test="--test"
            install_dir="../test/"        
        ;;
        -r|--force) force="--force"               
        ;;
        -r|--labname) labname="--labname $2"               
        ;;
        -r|--dev) dev="--dev"               
        ;;
        *) break
    esac
    shift
done

curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py

python3 -m pip install --upgrade pip
python3 -m pip install virtualenv
python3 -m virtualenv ../.venv --python=python3
source ../.venv/bin/activate

python3 -m pip install -r "requirements.txt"
python3 ./src/gpm.py --install $repo $labname $test $force $dev

find ${install_dir}gws/bricks -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
find ${install_dir}gws/sandbox -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
find ${install_dir}gws/labs -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;

find ${install_dir}user/bricks -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
find ${install_dir}user/sandbox -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
find ${install_dir}user/labs -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;