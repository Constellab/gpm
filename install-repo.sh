repo="all"
test=""
force=""
labname=""
dev=""
docker="no"

root_dir="../"
gwsdir="${root_dir}gws/"
userdir="${root_dir}user/"
userdir_is_locked="no"

while :; do
    case $1 in
        -b|--brick) repo=$2         
        ;;
        -t|--test) 
            test="--test"
            if [ $userdir_is_locked == "no" ]; then
                root_dir="../tests/"    
                gwsdir="${root_dir}gws/"
                userdir="${root_dir}user/"
            else
                root_dir="../tests/"    
                gwsdir="${root_dir}gws/"
                #do not update $userdir
            fi
        ;;
        -r|--force) force="--force"               
        ;;
        --labname) labname="--labname $2"               
        ;;
        --dev) dev="--dev"               
        ;;
        --docker) docker="yes"               
        ;;
        --user-dir) 
            userdir="$2"  
            userdir_is_locked="yes"            
        ;;
        *) break
    esac
    shift
done

if [ $docker == "no" ]; then
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py

    python3 -m pip install --upgrade pip
    python3 -m pip install virtualenv
    python3 -m virtualenv ${root_dir}.venv --python=python3
    . ${root_dir}.venv/bin/activate
fi

python3 -m pip install -r "requirements.txt"
python3 ./src/gpm.py --install $repo $labname $test $force $dev

find ${gwsdir}bricks -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
find ${gwsdir}sandbox -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
find ${gwsdir}labs -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;

find ${userdir}bricks -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
find ${userdir}sandbox -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;
find ${userdir}labs -name 'requirements.txt' -exec python3 -m pip install -r '{}' \;