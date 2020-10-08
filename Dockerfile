FROM ubuntu

LABEL maintainer="Admin <admin@gencovery.com>"
 
ENV LAB_NAME mylab
ENV APP_DIR /app/gws
ENV GPM_DIR /app/gws/gpm
ENV GWS_DIR /app/gws/gws

ENV USER_DIR /app/gws/user
ENV LAB_DIR /app/gws/labs/mylab

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

# bazel
#RUN chmod +x ./sh/install_bazel.sh
#RUN ./sh/install_bazel.sh
# dlib
#COPY ./sh/install_dlib.sh ./extern/dlib-cpp
#GPM_DIR ${GPM_DIR}/extern/dlib-cpp
#RUN chmod +x ./sh/install_dlib.sh
#RUN ./sh/install_dlib.sh

RUN chmod 755 docker-entrypoint.sh

ENTRYPOINT [ "/app/gws/gpm/docker-entrypoint.sh" ]
CMD [ "/app/gws/gws", "/app/gws/user", "/app/gws/labs/mylab", "mylab" ]

#CMD python3 ${LAB_DIR}/manage.py --runserver