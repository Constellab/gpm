# GWS Package Manager

This python module allows to manage gws packages. It is namely used to deploy lab docker on unix instances.

## How to?

### Requirements

* OS: Ubuntu (>= 20.04)
  * For GPU docker use Ubuntu 20.04 only!

### Step 1: Prepare the server instance

Run the following commands

```
cd utils
. prepare-server.sh
```

#### NVIDIA GPU: cuda driver

If NVIDA-GPU is detected on the instance, all GPU drivers will automatically be installed using sub-script `./utils/gpu/install-cuda.sh`. The computer will reboot after this command.

#### Disk mount

If a disk partition `sdb` is detected, the disk will be automatically formated and mounted on the server using `./utils/gpu/install-cuda.sh`.

We make the assumption here that `sda` is the default disk partition of the isntance and `sdb` is therefore the second one. If `sdb` is alredy formated or mounted, it won't be reformated.

### Step 2: Install the docker

The script `install.sh` will search for a config file `.config.json` to deploy the docker. A template config file exists in `./config/template_config.json`. It explains, all the configuration that are needed to create a new docker.

#### Create the config file

Run

```
cp ./config/template_config.json .config.json
```

Update the following fields in file `.config.json`

```
{
...
"start_mode": "prod",
"virtual_host": "test.gencovery.io",
"uri": "",
"token": "",
...
}
```   
* `start_mode` value must be set to `prod` by default. Set the value to `dev` to configure the lab in development mode.
* `virtual_host` is the base URL of the domain of the lab. If the virtual host is `test.gencovery.io` then
  * the Main lab will accessible via `lab.test.gencovery.io`
  * the Jupyter lab will accessible via `jlab.test.gencovery.io` (WILL DEPRECATED SOON)
  * the VScode lab will accessible via `vlab.test.gencovery.io`
  
  All the subdomains will be automatically configured with approriate HTTPS certificats behind a `nginx` proxy.

* `uri` is the unique identifier of the lab
* `token` is the private token of the lab used for user authentications. It MUST be kept private.

* DNS configuration:
In this case, the domain `*.test.gencovery.io` must be configured on the the public IP of the instance otherwise the certficats will not be properly created. The DNS configuration is done through OVHcloud servers.

#### Build and install the docker

```
. install.sh
```

The config file `.config.sh` is used by default.

#### Rebuild the docker

```
. install.sh --build
```

The config file `.config.sh` is used by default.

## Manual usages

### Docker installation

To build the docker image, use the file ```install.sh```. The docker compose template files is in ```./docker```.

Command: ```install.sh [--build] [--config </config/file/path.json>]```.

#### Example

* Build and run in production mode

```sh
. install.sh --build --config ./config/config.json
```

### Misc: raw update of bricks

Command: ```get-bricks.sh --config </config/file/path.json> --app-dir </absolute/path> [--lab-name <name>] [--prod | --dev]```

* OPTION ```--app-dir```. The installation path of the application
* OPTION ```--config```. The path of the configuration file (JSON file). Defaults to ```./config/config.json```. A default config file is given by ```./config/config.json```
* OPTION ```--lab-name```. The name of lab used as entrypoint. Defaults to ```main```
* OPTION ```--prod``` or ```--dev``` to install in production or development mode. Defaults to ```--prod```.

#### Example

```sh
. get-bricks.sh --app-dir </user/work/dir> --config ./config/config.json --lab-name foo
```

* OPTION ```--lab-name``` is the name of lab used as entrypoint. Defaults to ```main```

### Setup local development

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

#### Open a brick in docker environment

VS Code creae a docker container for your environment. You can open another folder than gpm in this environment.

To do this :

* Open the folder you want (for example the gws brick) it vs code.
* Click on the bottom left in the remote container button
* Select "Attach to running container"
* Select your development container (it must be running)
* Once your project is opened you have to select the folder to open inside linux environment. Click on open folder and navigate to **/workspaces/lab/** (this is where the brick are generated inside the docker).
You will find the different brick and you'll be able to able the folder you want. VS Code should remember this afterward.
