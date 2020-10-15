FROM ubuntu

LABEL maintainer="Admin <admin@gencovery.com>"
 
ARG APP_DIR
ARG LAB_NAME
ARG SERVER_ARGS

ENV APP_DIR /app/gws
ENV WORK_DIR ${APP_DIR}/gpm
ENV GWS_DIR ${APP_DIR}/gws
ENV EXTERN_DIR ${APP_DIR}/gws/externs
ENV USER_DIR ${APP_DIR}/user
ENV LAB_DIR ${USER_DIR}/labs/${LAB_NAME}

ADD . ${WORK_DIR}
WORKDIR ${WORK_DIR}

# install python, pip and venv
RUN chmod +x ./src/install_python.sh
RUN bash ./src/install_python.sh
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3 get-pip.py
RUN python3 -m pip install --upgrade pip
# RUN python3 -m pip install virtualenv
# ENV VIRTUAL_ENV=/opt/venv
# RUN python3 -m virtualenv $VIRTUAL_ENV --python=python3
# ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# install app
RUN chmod +x ./src/askpass.sh
RUN chmod +x ./gpm.sh

RUN bash ./gpm.sh --install-gws ${GWS_DIR} --lab-name ${LAB_NAME} --docker

# bazel
#RUN chmod +x ./sh/install_bazel.sh
#RUN bash ./sh/install_bazel.sh

# dlib
#COPY ./sh/install_dlib.sh ${EXTERN_DIR}/dlib-cpp
#WORK_DIR ${EXTERN_DIR}/dlib-cpp
#RUN chmod +x ./sh/install_dlib.sh
#RUN bash ./sh/install_dlib.sh

EXPOSE 3000 
CMD python3 ${LAB_DIR}/manage.py --runserver ${SERVER_ARGS}