
# install python an pip
sudo apt -y install python3
python -m install pip 
python -m pip install --upgrade pip

# instal virtual env
python -m pip install virtualenv
virtualenv .venv --python=python3
.venv/bin/pip install -r requirements.txt

