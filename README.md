# Gencovery Package Manager (GPM)

This repository allows managing Gencovery Web Services packages. It is used to create docker images to easily deploy GLab.

* Shell script ```init_lab.sh``` is run by the dockerfile entrypoint

* Python script ```init_lab.py``` is called by the ```init_lab.sh``` and allows pulling and intalling from Pip and Git any library described in an environment file ```config.json``` as given in folder ```tests/fixtures/config.json```

## Testing

### Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file at project root with the following variables (optional for git pull tests):
   ```
   COMMUNITY_API_URL=<your_api_url>
   ```

### Running Tests

The project uses pytest for testing. Tests are organized in a standard structure:

```
tests/
├── unit/              # Unit tests
├── integration/       # Integration tests
├── fixtures/          # Test data and configuration
└── conftest.py        # Shared fixtures
```

**Run all tests:**
```bash
pytest
```

**Run specific test categories:**
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run tests in a specific file
pytest tests/unit/test_gpm.py

# Run tests with verbose output
pytest -v

# Run tests with coverage report (requires pytest-cov)
pytest --cov=init --cov-report=html
```

**Run tests in VS Code:**
- Use the Testing sidebar (flask icon)
- Tests are automatically discovered based on the `pytest.ini` configuration
- Click individual tests or test classes to run them

### Test Markers

Tests are automatically marked based on their location and can also use custom markers:

- `@pytest.mark.unit` - Unit tests (auto-applied to tests/unit/*)
- `@pytest.mark.integration` - Integration tests (auto-applied to tests/integration/*)
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.requires_network` - Tests requiring network access
- `@pytest.mark.requires_git` - Tests requiring git operations

**Filter tests by markers:**
```bash
# Skip slow tests
pytest -m "not slow"

# Run only network tests
pytest -m requires_network
``` 

## Testing the docker images

Testing the glab image locally : ```docker build -t glab:latest -f ./dockerfile/glab/Dockerfile .```
Testing the codelab image locally : ```docker build -t codelab:codelab -f ./dockerfile/codelab/Dockerfile .```

Coding using the dev-env image : ```docker build -t lab-dev-env -f ./dockerfile/lab-dev-env/Dockerfile .```

To run and tests the images, see lab-configurer repository.

## Testing GPU the docker images

Testing the glab image locally : ```docker build --build-arg IMAGE="nvidia/cuda:12.4.1-runtime-ubuntu22.04" -t glab:gpu -f ./dockerfile/glab/Dockerfile .```

Testing the codelab image locally : ```docker build --build-arg IMAGE="glab:gpu" -t local-codelab -f ./dockerfile/codelab/Dockerfile .```

## Building with buildx for multi-arch

From : https://itnext.io/building-multi-cpu-architecture-docker-images-for-arm-and-x86-2-building-in-gitlab-ci-295966b7185d

Create a new docker context for builder instance to use
```docker context create builder-context```

Create a builder instance named "builderx"
```docker buildx create --name builderx --driver docker-container --use builder-context```


```docker buildx build -t glab:latest -f ./dockerfile/glab/Dockerfile --platform linux/amd64,linux/arm64 .```