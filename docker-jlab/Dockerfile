
FROM ubuntu
LABEL maintainer="Admin <admin@gencovery.com>"

ENV WORK_DIR /app/gpm

ADD ./ ${WORK_DIR}
WORKDIR ${WORK_DIR}

# install python
RUN apt-get -y update
RUN apt-get -y install python3
RUN apt-get -y install python3-distutils
RUN apt-get -y install python3-pip
RUN apt-get -y install git

# install pip
#RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
#RUN python3 get-pip.py
#RUN python3 -m pip install --upgrade pip
#RUN python3 -m pip install --upgrade setuptools

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install jupyterlab
RUN python3 -m pip install ipywidgets
RUN jupyter nbextension enable --py widgetsnbextension

EXPOSE 8888

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "--runserver" ]