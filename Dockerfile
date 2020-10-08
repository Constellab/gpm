FROM ubuntu

LABEL maintainer="Gencovery Admin <admin@gencovery.com>"
 
ARG APPDIR
ARG USERDIR
ARG LABNAME

ENV WORKDIR ${APPDIR}/gpm
ENV GWSDIR ${APPDIR}/gws
ENV LABDIR ${USERDIR}/labs/${LABNAME}

ADD . ${WORKDIR}

WORKDIR ${WORKDIR}

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
RUN bash ./gpm.sh --gws-dir ${GWSDIR} --user-dir ${USERDIR} --lab-name ${LABNAME} --docker

# bazel
#RUN chmod +x ./sh/install_bazel.sh
#RUN ./sh/install_bazel.sh

# dlib
#COPY ./sh/install_dlib.sh ./extern/dlib-cpp
#WORKDIR ${WORKDIR}/extern/dlib-cpp
#RUN chmod +x ./sh/install_dlib.sh
#RUN ./sh/install_dlib.sh

WORKDIR ${LABDIR}

RUN ls -al
RUN ls ../ -al

CMD python3 manage.py --runserver