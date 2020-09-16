
#!/bin/bash

# install python3
apt-get -y update
apt-get -y install python3
apt-get -y install python3-distutils
apt-get -y install python3-pip
apt-get -y install curl


apt-get -y install git

# install pip
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade setuptools

# python requirements
python3 -m pip install -r requirements.txt
