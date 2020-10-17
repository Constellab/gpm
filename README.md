# GWS package manger

This python module allows to manage gws bricks an labs

## Raw installation (without docker)

To install the packages without docker, use the file ```install-raw.sh```.

Command: ```install-raw.sh --config </config/file/path.json> --app-dir </absolute/path> [--lab-name <name>] [--prod | --dev]```

* OPTION ```--app-dir```. The installation path of the application
* OPTION ```--config```. The path of the configuration file (JSON file). A default config file is given in folder ```./config/```
* OPTION ```--lab-name```. The name of lab used as entrypoint. Defaults to ```main```
* OPTION ```--prod``` or ```--dev``` to install in production or development mode. Defaults to ```--prod```.



### Example

```
. install-raw.sh --app-dir /Users/djomangan/Dev/docker --config ./config/config.json --lab-name foo
```

* OPTION ```--lab-name``` is the name of lab used as entrypoint. Defaults to ```main```

## Docker installation

To build the docker image, use the file ```install-docker.sh```. The docker compose template files is in ```./docker```.

Command: ```install-docker.sh --config </config/file/path.json> --app-dir </absolute/path> [--test] [--lab-name <name>] [--prod | --dev]```.
The options are the same as in the raw installation. Supplementary options are:

* OPTION ```--test``` to test the build process. Only basic files will be compiled in development mode (```--dev``` forced). The docker will not be runnable.

### Environment variables

Docker compose variables:
```yml
environment:
  - APP_DIR: ...
  - LAB_NAME: ...
  - START_MODE: ...
```
* ```WORKSPACE```, defaults to ```/home/ubuntu/work```. It is the workspace of the user. This folder is mounted as a volume ans and will contain all the necessary bricks, labs, externs libs, data and tmp files.
* ```LAB_NAME```, default to ```main```. It is the main user lab used as entrypoint. This lab must exists in the labs sub-directory in the ```WORKSPACE```.
* ```START_MODE```, defaults to ```--prod```. Allows starting the server in production (```--prod```) or development (```--dev```) mode. No token is required to access the lab in development. 


WARNING: For security reasons, nether starts the server in developement mode while using it in production mode. Everyone could access it from internet.

### Example

```
. install-docker.sh --test --app-dir /Users/djomangan/Dev/docker --config ./config/config.json --lab-name foo
```
# Push/pull bricks and labs

Not yet implemented

* ```pull.sh --pull <brick-name>``` to pull a brick (or a lab). The docker image must be rebuild to update changes (run ```install-docker``` to rebuild).
* ```push.sh --push <brick-name> <tag>``` to push a brick (or a lab) using a tag name.