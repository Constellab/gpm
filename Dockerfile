FROM ubuntu

LABEL maintainer="Gencovery Admin <admin@gencovery.com>"
 
ARG APPDIR
ARG LABNAME
ARG USERDIR

ENV WORKDIR ${APPDIR}
ENV LABDIR ${USERDIR}/labs/${LABNAME}

ADD . ${WORKDIR}

WORKDIR ${WORKDIR}

RUN ls -al

RUN chmod +x ./src/install_python.sh
RUN ./src/install_python.sh

RUN ls -al

# install python and venv
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3 get-pip.py
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install virtualenv

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m virtualenv $VIRTUAL_ENV --python=python3
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN chmod +x ./src/askpass.sh
RUN chmod +x ./install-repo.sh --docker --user-dir ${USERDIR}
RUN ./install-repo.sh --labname ${LABNAME} 
RUN ls -al

# bazel
#RUN chmod +x ./sh/install_bazel.sh
#RUN ./sh/install_bazel.sh

# dlib
#COPY ./sh/install_dlib.sh ./extern/dlib-cpp
#WORKDIR ${WORKDIR}/extern/dlib-cpp
#RUN chmod +x ./sh/install_dlib.sh
#RUN ./sh/install_dlib.sh

WORKDIR ${LABDIR}
CMD python3 manage.py --runserver