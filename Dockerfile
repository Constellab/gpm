FROM ubuntu

LABEL maintainer="Admin <admin@gencovery.com>"

# ENV VIRTUAL_HOST mylab.lab.gencovery.com
# ENV VIRTUAL_HOST_JLAB  jlab.mylab.lab.gencovery.com
ENV WORK_DIR /app/gpm
ENV GWS_EXTERN_DIR /app/gws/gws/externs

ADD . ${WORK_DIR}
WORKDIR ${WORK_DIR}

# install python, pip and venv
RUN chmod +x ./src/install_python.sh
RUN bash ./src/install_python.sh
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3 get-pip.py
RUN python3 -m pip install --upgrade pip

# RUN echo -e "#Added by Gencovery" >> /etc/hosts
# RUN echo -e "127.0.0.1    ${VIRTUAL_HOST}" >> /etc/hosts
# RUN echo -e "127.0.0.1    jlab.${VIRTUAL_HOST}" >> /etc/hosts
# RUN echo -e "#End section" >> /etc/hosts

# bazel
#RUN chmod +x ./sh/install_bazel.sh
#RUN bash ./sh/install_bazel.sh

# dlib
#COPY ./sh/install_dlib.sh ${GWS_EXTERN_DIR}/dlib-cpp
#WORK_DIR ${GWS_EXTERN_DIR}/dlib-cpp
#RUN chmod +x ./sh/install_dlib.sh
#RUN bash ./sh/install_dlib.sh

EXPOSE 3000 
EXPOSE 8888

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "--runserver", "main" ]