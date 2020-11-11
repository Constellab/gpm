
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

# install jupyter lab
RUN python3 -m pip install jupyterlab
RUN python3 -m pip install ipywidgets

# install bazel
RUN sudo apt install curl gnupg
RUN curl -fsSL https://bazel.build/bazel-release.pub.gpg | gpg --dearmor > bazel.gpg
RUN sudo mv bazel.gpg /etc/apt/trusted.gpg.d/
RUN echo "deb [arch=amd64] https://storage.googleapis.com/bazel-apt stable jdk1.8" | sudo tee /etc/apt/sources.list.d/bazel.list
RUN apt-get -y install bazel
RUN apt-get -y update
RUN apt-get -y full-upgrade

# install C++ dev tools
RUN apt-get -y install g++ unzip zip
RUN apt-get -y install build-essential cmake pkg-config
RUN apt-get -y install libx11-dev libatlas-base-dev
RUN apt-get -y install libgtk-3-dev libboost-python-dev
RUN apt-get -y install libopenblas-dev liblapack-dev

# build and install dlib
WORKDIR ${GWS_EXTERN_DIR}/dlib-cpp
RUN mkdir build
RUN cd build
RUN cmake -DUSE_AVX_INSTRUCTIONS=ON -DBUILD_SHARED_LIBS=1 ..
RUN cmake --build . --config Release
RUN make
RUN make install
RUN ldconfig

WORKDIR ${WORK_DIR}

EXPOSE 8888

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "--runserver" ]