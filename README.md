# GWS Package Manager

This python module allows to manage gws packages (i.e. bricks and labs packages)


## Install docker first

```
cd utils
. install-docker.sh
```

The command will install any GPU library and prepare the computer to run docker with GPU capabilities. GPU capabilities are possible for CUDA. The computer will reboot after this command.

## Docker installation

To build the docker image, use the file ```install.sh```. The docker compose template files is in ```./docker```.

Command: ```install.sh [--build] [--config </config/file/path.json>]```.


### Example

* Build and run in production mode

```
. install.sh --build --config ./config/config.json
```

* Build and run in dev mode

```
. install.sh --dev --app-dir </user/work/dir> --config ./config/config.json --lab-name foo
```

## Misc: raw update of bricks

Command: ```get-bricks.sh --config </config/file/path.json> --app-dir </absolute/path> [--lab-name <name>] [--prod | --dev]```

* OPTION ```--app-dir```. The installation path of the application
* OPTION ```--config```. The path of the configuration file (JSON file). Defaults to ```./config/config.json```. A default config file is given by ```./config/config.json```
* OPTION ```--lab-name```. The name of lab used as entrypoint. Defaults to ```main```
* OPTION ```--prod``` or ```--dev``` to install in production or development mode. Defaults to ```--prod```.

### Example

```
. get-bricks.sh --app-dir </user/work/dir> --config ./config/config.json --lab-name foo
```

* OPTION ```--lab-name``` is the name of lab used as entrypoint. Defaults to ```main```
