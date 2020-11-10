FROM ubuntu
LABEL maintainer="Admin <admin@gencovery.com>"

ENV WORK_DIR /app/gpm
ENV GWS_EXTERN_DIR /app/gws/.gws/externs

ADD ./ ${WORK_DIR}
WORKDIR ${WORK_DIR}

# install python
RUN apt-get -y update
RUN apt-get -y install python3
RUN apt-get -y install python3-distutils
RUN apt-get -y install git
RUN apt-get -y install curl

# install pip
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3 get-pip.py
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --upgrade setuptools

# bazel
#RUN chmod +x ./sh/install-bazel.sh
#RUN bash ./sh/install-bazel.sh

# dlib
#COPY ./sh/install-dlib.sh ${GWS_EXTERN_DIR}/dlib-cpp
#WORK_DIR ${GWS_EXTERN_DIR}/dlib-cpp
#RUN chmod +x ./sh/install-dlib.sh
#RUN bash ./sh/install-dlib.sh

EXPOSE 3000 

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "--runserver", "main" ]