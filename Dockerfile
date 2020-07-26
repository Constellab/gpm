FROM ubuntu
ARG USER
ARG WORKDIR
ARG GIT_USER 
ARG GIT_PWD 

ENV WORKDIR /usr/src/gws
ENV APPDIR ${WORKDIR}/app

ADD . ${WORKDIR}

WORKDIR ${WORKDIR}

RUN ls -al

RUN chmod +x install-python.sh
RUN ./install-python.sh

RUN ls -al

RUN chmod +x askpass.sh
RUN python3 get-gws.py              \
    --user ${USER}                  \
    --output ${APPDIR}              \
    --git-user ${GIT_USER}          \
    --git-pwd ${GIT_PWD}

RUN ls -al

# bazel
#RUN chmod +x install-bazel.sh
#RUN ./install-bazel.sh

# dlib
#COPY install-dlib.sh ./extern/dlib-cpp
#WORKDIR ${WORKDIR}/extern/dlib-cpp
#RUN chmod +x install-dlib.sh
#RUN ./install-dlib.sh

#EXPOSE 3000

WORKDIR ${APPDIR}/app/app-py/
CMD python3 manage.py --runserver