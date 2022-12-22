# Gencovery Package Manager (GPM)

This repository allows managing Gencovery Web Services packages. It is used to create docker images to easily deploy GLab.

* Shell script ```gpm.sh``` is run by the docerfile entrypoint

* Python script ```gpm.py``` is called by the ```gpm.sh``` and allows pulling and intalling from Pip and Git any library described in an environment file ```config.json``` as given in folder ```tests/config.json```

## Testing

For testing, use the VsCode testing extension and run test gpm tests. 
Create a .env file at project root with GWS_GIT_LOGIN and GWS_GIT_PWD (using astroyboy account or you own account) env variables to test the git pull.

Testing the glab image locally : ```docker build -t glab:latest -f .\dockerfile\glab\Dockerfile .```
Testing the codelab image locally : ```docker build -t local-codelab -f .\dockerfile\codelab\Dockerfile .```