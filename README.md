# GWS Package Manager

This python module allows to manage gws packages (i.e. bricks and labs packages)

## Install docker first

```sh
cd utils
. install-docker.sh
```

The command will install any GPU library and prepare the computer to run docker with GPU capabilities. GPU capabilities are possible for CUDA. The computer will reboot after this command.

## Docker installation

To build the docker image, use the file ```install.sh```. The docker compose template files is in ```./docker```.

Command: ```install.sh [--build] [--config </config/file/path.json>]```.

### Example

* Build and run in production mode

```sh
. install.sh --build --config ./config/config.json
```

* Build and run in dev mode

```sh
. install.sh --dev --app-dir </user/work/dir> --config ./config/config.json --lab-name foo
```

## Misc: raw update of bricks

Command: ```get-bricks.sh --config </config/file/path.json> --app-dir </absolute/path> [--lab-name <name>] [--prod | --dev]```

* OPTION ```--app-dir```. The installation path of the application
* OPTION ```--config```. The path of the configuration file (JSON file). Defaults to ```./config/config.json```. A default config file is given by ```./config/config.json```
* OPTION ```--lab-name```. The name of lab used as entrypoint. Defaults to ```main```
* OPTION ```--prod``` or ```--dev``` to install in production or development mode. Defaults to ```--prod```.

### Example

```sh
. get-bricks.sh --app-dir </user/work/dir> --config ./config/config.json --lab-name foo
```

* OPTION ```--lab-name``` is the name of lab used as entrypoint. Defaults to ```main```

## Setup local development

To work on gws locally, I recommend using VS code and remote container.

First install the remote container VS Code extension. More information can be found here : https://code.visualstudio.com/docs/remote/containers

If you are in windows you'll need to setup WSL 2.

Then update the ```.devcontainer/devcontainer.json``` file and change the mo
unt source absolute path to a path in your computer where you want the bricks to be installed.

```json
"mounts": ["source=C:\\Users\\Benjamin\\Documents\\Project\\Gencovery\\lab2,target=/workspaces/lab,type=bind,consistency=cached"]
```

Once done, you are ready to open the project in a remote docker container :

* In VS Code, open the gpm repository
* Click on the bottom left in the remote container button
* In the appeared list, click on "Reopen in Container"

 This will reoppen the projet in a docker and install all the ubuntu dependencies. Once ubuntu is setup it will install and the pipe and bricks dependencies. 

and that's it, your VS code docker environment is configured

### Open a brick in docker environment

VS Code creae a docker container for your environment. You can open another folder than gpm in this environment.

To do this :

* Open the folder you want (for example the gws brick) it vs code.
* Click on the bottom left in the remote container button
* Select "Attach to running container"
* Select your development container (it must be running)
* Once your project is opened you have to select the folder to open inside linux environment. Click on open folder and navigate to **/workspaces/lab/** (this is where the brick are generated inside the docker).
You will find the different brick and you'll be able to able the folder you want. VS Code should remember this afterward.
