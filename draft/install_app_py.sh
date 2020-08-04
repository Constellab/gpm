
# install python an pip
sudo apt -y install python3
python3 -m install pip 
python3 -m pip install --upgrade pip

# instal virtual env
python3 -m pip install virtualenv
virtualenv .venv --python=python3
.venv/bin/pip install -r requirements.txt

