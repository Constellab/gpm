FROM ubuntu

LABEL maintainer="Gencovery Admin <admin@gencovery.com>"

ENV LABNAME mylab

ENV GWSDIR /home/ubuntu/work
ENV WORKDIR ${GWSDIR}/gpm
ENV LABDIR ${GWSDIR}/user/labs/${LABNAME}

ADD . ${WORKDIR}

WORKDIR ${WORKDIR}

RUN ls -al

RUN chmod +x ./src/install_python.sh
RUN ./src/install_python.sh

RUN ls -al

RUN chmod +x ./src/askpass.sh
RUN ./install.sh --labname ${LABNAME}  
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