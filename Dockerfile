FROM ubuntu

LABEL maintainer="Admin <admin@gencovery.com>"
 
ARG APP_DIR
ARG LAB_NAME

ENV GPM_DIR ${APP_DIR}/gpm
ENV GWS_DIR ${APP_DIR}/gws

ENV USER_DIR ${APP_DIR}/user
ENV LAB_DIR ${USER_DIR}/labs/${LAB_NAME}

#ENV TMP_USER_DIR ${APP_DIR}/tmp_user

VOLUME ${USER_DIR}

ADD . ${GPM_DIR}
WORKDIR ${GPM_DIR}

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

#RUN bash ./gpm.sh --install --gws-dir ${GWS_DIR} --user-dir ${USER_DIR} --lab-name ${LAB_NAME} --docker

#RUN ls ${TMP_USER_DIR} -al
#RUN cp -r ${TMP_USER_DIR}/** ${USER_DIR}
#RUN rm -rf ${TMP_USER_DIR}

# bazel
#RUN chmod +x ./sh/install_bazel.sh
#RUN ./sh/install_bazel.sh

# dlib
#COPY ./sh/install_dlib.sh ./extern/dlib-cpp
#GPM_DIR ${GPM_DIR}/extern/dlib-cpp
#RUN chmod +x ./sh/install_dlib.sh
#RUN ./sh/install_dlib.sh

COPY docker-entrypoint.sh ${APP_DIR}/entrypoint.sh
ENTRYPOINT [ "${APP_DIR}/entrypoint.sh" ]
CMD [ "${GWS_DIR}", "${USER_DIR}", "${LAB_DIR}", "${LAB_NAME}" ]

#CMD python3 ${LAB_DIR}/manage.py --runserver