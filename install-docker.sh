
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

bash gpm.sh --install-user /home/ubuntu/work/

if [[ $test == "yes" ]]; then
    cd ./docker-test
else
    cd ./docker
fi

docker-compose up -build