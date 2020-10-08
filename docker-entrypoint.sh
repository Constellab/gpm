
GPM_DIR=$1
GWS_DIR=$2
USER_DIR=$3
LAB_DIR=$4
LAB_NAME=$5

if [[ -f "${LAB_DIR}/manage.py" ]]; then
    python3 ${LAB_DIR}/manage.py --runserver
else
    bash ${GPM_DIR}/gpm.sh --install --gws-dir ${GWS_DIR} --user-dir ${USER_DIR} --lab-name ${LAB_NAME} --docker
    python3 ${LAB_DIR}/manage.py --runserver
fi


