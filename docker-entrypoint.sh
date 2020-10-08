
GWS_DIR=$1
USER_DIR=$2
LAB_DIR=$3
LAB_NAME=$4

if [[ -f "${LAB_DIR}/manage.py" ]]; then
    python3 ${LAB_DIR}/manage.py --runserver
else
    bash ./gpm.sh --install --gws-dir ${GWS_DIR} --user-dir ${USER_DIR} --lab-name ${LAB_NAME} --docker
    python3 ${LAB_DIR}/manage.py --runserver
fi


