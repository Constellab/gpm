# GWS Package Manager

This python module allows to manage gws packages (i.e. bricks and labs packages)

## Docker build and start

To build the docker image, use the file ```start-docker.sh```. The docker compose template files is in ```./docker```.

Command: ```start-docker.sh <name> [option] --config </config/file/path.json>```.
* Name can be ```gws``` (default), ```jlab```, ```nginx``` or ```all``` (to start all the dockers)
* Options:
  * ```--build``` to re-build
  * ```-d``` or ```--detach``` to start in detached mode

### Environment variables

Docker compose variables:
```yml
environment:
  - APP_DIR: ...
  - LAB_NAME: ...
  - START_MODE: ...
```
* ```LAB_NAME```, default to ```main```. It is the main user lab used as entrypoint. This lab must exists in the labs sub-directory in the ```WORKSPACE```.
* ```START_MODE```, defaults to ```--prod```. Allows starting the server in production (```--prod```) or development (```--dev```) mode. No token is required to access the lab in development. 


WARNING: For security reasons, nether starts the server in developement mode while using it in production mode. Everyone could access it from internet.

### Example

* Build and run in dev mode
```
. start-docker.sh --app-dir </user/work/dir> --config ./config/config.json --lab-name foo --lab-token 12345abcd --jlab-token 12345abcd
```

* Build and run in production mode

```
. start-docker.sh --dev --app-dir </user/work/dir> --config ./config/config.json --lab-name foo
```

## Raw installation (without docker)

To install the packages without docker, use the file ```install-raw-app.sh```.

Command: ```install-raw-app.sh --config </config/file/path.json> --app-dir </absolute/path> [--lab-name <name>] [--prod | --dev]```

* OPTION ```--app-dir```. The installation path of the application
* OPTION ```--config```. The path of the configuration file (JSON file). Defaults to ```./config/config.json```. A default config file is given by ```./config/config.json```
* OPTION ```--lab-name```. The name of lab used as entrypoint. Defaults to ```main```
* OPTION ```--prod``` or ```--dev``` to install in production or development mode. Defaults to ```--prod```.

### Example

```
. install-raw-app.sh --app-dir </user/work/dir> --config ./config/config.json --lab-name foo
```

* OPTION ```--lab-name``` is the name of lab used as entrypoint. Defaults to ```main```
