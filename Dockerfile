FROM ubuntu

LABEL maintainer="Admin <admin@gencovery.com>"
 
ARG APP_DIR
ARG LAB_NAME

ENV WORK_DIR ${APP_DIR}/gpm
ENV GWS_DIR ${APP_DIR}/gws
ENV USER_DIR ${APP_DIR}/user
ENV LAB_DIR ${USER_DIR}/labs/${LAB_NAME}

ADD . ${WORK_DIR}
WORKDIR ${WORK_DIR}

VOLUME ${USER_DIR}

# install python, pip and venv
RUN chmod +x ./src/install_python.sh
RUN bash ./src/install_python.sh
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3 get-pip.py
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install virtualenv
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m virtualenv $VIRTUAL_ENV --python=python3
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# install app
RUN chmod +x ./src/askpass.sh
RUN chmod +x ./gpm.sh
RUN bash ./gpm.sh --install --gws-dir ${GWS_DIR} --user-dir ${USER_DIR} --lab-name ${LAB_NAME} --docker

# bazel
#RUN chmod +x ./sh/install_bazel.sh
#RUN ./sh/install_bazel.sh

# dlib
#COPY ./sh/install_dlib.sh ./extern/dlib-cpp
#WORK_DIR ${WORK_DIR}/extern/dlib-cpp
#RUN chmod +x ./sh/install_dlib.sh
#RUN ./sh/install_dlib.sh

WORKDIR ${LAB_DIR}

RUN ls ${LAB_DIR} -al
RUN ls ${USER_DIR} -al

CMD python3 ${USER_DIR}/manage.py --runserver