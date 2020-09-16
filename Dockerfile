FROM ubuntu

LABEL maintainer="Gencovery <admin@gencovery.com>"
ARG USER
ARG LAB

ENV WORKDIR ../

ENV GPM_DIR ./gpm
ENV GWS_DIR ./gws
ENV USER_DIR ./users/${USER}

ADD . ${WORKDIR}

# create gws dirs
WORKDIR ${GWS_DIR}
RUN chmod +x ../gpm/sh/make_dirs.sh
RUN ../gpm/sh/make_dirs.sh

# create user dirs
WORKDIR ${USER_DIR}
RUN chmod +x ../../gpm/sh/make_dirs.sh
RUN ../../gpm/sh/make_dirs.sh

WORKDIR ${WORKDIR}

RUN ls -al

WORKDIR ${GPM_DIR}
RUN chmod +x ./sh/install_python.sh
RUN ./sh/install_python.sh

RUN ls -al

RUN chmod +x ./sh/askpass.sh
RUN python3 gpm.py              \
    --pull all                  \
    --gwsdir ${GWS_DIR}

RUN ls -al

# bazel
#RUN chmod +x ./sh/install_bazel.sh
#RUN ./sh/install_bazel.sh

# dlib
#COPY ./sh/install_dlib.sh ./extern/dlib-cpp
#WORKDIR ${WORKDIR}/extern/dlib-cpp
#RUN chmod +x ./sh/install_dlib.sh
#RUN ./sh/install_dlib.sh

#EXPOSE 3000

WORKDIR ${USER_DIR}/labs/glab/
CMD python3 manage.py --runserver