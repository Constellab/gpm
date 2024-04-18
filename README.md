# Gencovery Package Manager (GPM)

This repository allows managing Gencovery Web Services packages. It is used to create docker images to easily deploy GLab.

* Shell script ```init_lab.sh``` is run by the docerfile entrypoint

* Python script ```init_lab.py``` is called by the ```init_lab.sh``` and allows pulling and intalling from Pip and Git any library described in an environment file ```config.json``` as given in folder ```tests/config.json```

## Testing

For testing, install dependencies with ```pip install -r requirements.txt```

Create a .env file at project root with COMMUNITY_API_URL and COMMUNITY_API_KEY (optional) env variables to test the git pull.

Use the VsCode testing extension and run test gpm tests. 

## Testing the docker images

Testing the glab image locally : ```docker build -t glab:latest -f ./dockerfile/glab/Dockerfile .```
Testing the codelab image locally : ```docker build -t local-codelab -f ./dockerfile/codelab/Dockerfile .```

Coding using the dev-env image : ```docker build -t local-dev-env -f ./dockerfile/dev-env/Dockerfile .```

To run and tests the images, see dockerlab repository.

## Building with buildx for multi-arch

From : https://itnext.io/building-multi-cpu-architecture-docker-images-for-arm-and-x86-2-building-in-gitlab-ci-295966b7185d

Create a new docker context for builder instance to use
```docker context create builder-context```

Create a builder instance named "builderx"
```docker buildx create --name builderx --driver docker-container --use builder-context```


```docker buildx build -t glab:latest -f ./dockerfile/glab/Dockerfile --platform linux/amd64,linux/arm64 .```