# Test Organization

This directory contains all tests for the GPM (Gencovery Package Manager) project.

## Directory Structure

```
tests/
├── .build/                 # Generated test artifacts (gitignored)
│   └── lab/               # Lab workspace created during test runs
├── unit/                  # Unit tests
│   ├── test_gpm.py       # GPM core functionality tests
│   └── test_pip_manager.py # Pip manager tests
├── integration/           # Integration tests (future)
├── fixtures/              # Test data and configuration
│   ├── config.json       # Test configuration for GPM
│   └── __init__.py
├── conftest.py           # Shared pytest fixtures
├── __init__.py
└── README.md             # This file
```

## Test Categories

### Unit Tests (`tests/unit/`)
Fast, isolated tests for individual components:
- **test_gpm.py**: Tests for GPM initialization, brick management, and configuration
- **test_pip_manager.py**: Tests for pip package installation, version conflict detection, and package grouping

### Integration Tests (`tests/integration/`)
Tests that verify interaction between components (to be added as needed)

### Fixtures (`tests/fixtures/`)
Shared test data and configuration files:
- **config.json**: Sample GPM configuration for testing

## Writing Tests

### Basic Test Structure

```python
import pytest

def test_something():
    """Test description."""
    # Arrange
    value = 1

    # Act
    result = value + 1

    # Assert
    assert result == 2
```

### Using Fixtures

Common fixtures are defined in [conftest.py](conftest.py):

```python
def test_with_temp_workspace(temp_workspace):
    """Test that uses a temporary workspace."""
    # temp_workspace is a Path object to a temporary directory
    test_file = temp_workspace / "test.txt"
    test_file.write_text("test content")
    assert test_file.exists()
```

### Available Fixtures

- `project_root`: Path to the project root directory
- `fixtures_dir`: Path to the fixtures directory
- `test_config_path`: Path to the test configuration file
- `temp_workspace`: Temporary directory for test files (cleaned up automatically)
- `clean_pip_packages`: List to track pip packages that should be cleaned up
- `test_build_dir`: Path to the test build directory
- `reset_gpm_env_vars`: Automatically resets environment variables (autouse)

### Test Markers

Mark tests to categorize them:

```python
@pytest.mark.slow
def test_long_running_operation():
    """This test takes a while."""
    pass

@pytest.mark.requires_network
def test_api_call():
    """This test needs internet access."""
    pass

@pytest.mark.requires_git
def test_git_clone():
    """This test needs git."""
    pass
```

## Running Tests

See the main [README.md](../README.md#testing) for detailed instructions on running tests.

Quick reference:
```bash
# All tests
pytest

# Specific file
pytest tests/unit/test_gpm.py

# Specific test
pytest tests/unit/test_gpm.py::TestGpmGlab::test_glab_initialization

# With markers
pytest -m "unit and not slow"

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

## Best Practices

1. **Keep tests independent**: Each test should work in isolation
2. **Use descriptive names**: Test names should clearly describe what they test
3. **Follow AAA pattern**: Arrange, Act, Assert
4. **Use fixtures for setup**: Leverage pytest fixtures for common setup
5. **Clean up resources**: Use fixtures with cleanup or context managers
6. **Mark slow tests**: Use `@pytest.mark.slow` for tests that take >1 second
7. **Test one thing**: Each test should verify one specific behavior
8. **Use temp directories**: Never write to the actual codebase during tests

## Test Coverage

To generate a coverage report:

```bash
# Install pytest-cov
pip install pytest-cov

# Run tests with coverage
pytest --cov=init --cov-report=html

# Open htmlcov/index.html in your browser
```

## Troubleshooting

### Tests can't find modules
Make sure you're running pytest from the project root directory.

### Old test artifacts
Clean the build directory:
```bash
rm -rf tests/.build/*
```

### Tests interfering with each other
Ensure you're using fixtures properly and not relying on global state.

### VS Code not discovering tests
1. Check that pytest is installed in your Python environment
2. Ensure [pytest.ini](../pytest.ini) is in the project root
3. Reload VS Code window (Cmd/Ctrl+Shift+P → "Reload Window")
