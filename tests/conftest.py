"""Pytest configuration and shared fixtures for all tests."""

import os
import shutil
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    """Get the fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def test_config_path(fixtures_dir) -> Path:
    """Get the path to the test configuration file."""
    return fixtures_dir / "config.json"


@pytest.fixture
def temp_workspace(tmp_path) -> Generator[Path, None, None]:
    """Create a temporary workspace that gets cleaned up after the test.

    This fixture creates a temporary directory for tests that need to
    create files or directories without affecting the actual codebase.
    """
    workspace = tmp_path / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)

    yield workspace

    # Cleanup
    if workspace.exists():
        shutil.rmtree(workspace, ignore_errors=True)


@pytest.fixture
def clean_pip_packages():
    """Fixture to track and clean up pip packages installed during tests.

    Yields a list that tests can append package names to.
    Cleans up those packages after the test completes.
    """
    packages_to_cleanup = []

    yield packages_to_cleanup

    # Cleanup installed packages
    if packages_to_cleanup:
        import subprocess
        cmd = ["pip", "uninstall", "-y"] + packages_to_cleanup
        subprocess.run(cmd, check=False, capture_output=True)


@pytest.fixture(scope="session")
def test_build_dir() -> Path:
    """Get the test build directory for generated artifacts."""
    return Path(__file__).parent / ".build"


@pytest.fixture(autouse=True)
def reset_gpm_env_vars():
    """Reset GPM environment variables before each test.

    This ensures tests don't interfere with each other through
    environment variable side effects.
    """
    original_env = os.environ.copy()

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


# Markers for test categorization
def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    # Register custom markers
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "requires_network: mark test as requiring network access"
    )
    config.addinivalue_line(
        "markers", "requires_git: mark test as requiring git operations"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test items during collection.

    Automatically mark tests based on their location:
    - tests/unit/* -> @pytest.mark.unit
    - tests/integration/* -> @pytest.mark.integration
    """
    for item in items:
        # Get the test file path relative to tests directory
        rel_path = Path(item.fspath).relative_to(Path(__file__).parent)

        # Auto-mark based on directory
        if "unit" in rel_path.parts:
            item.add_marker(pytest.mark.unit)
        elif "integration" in rel_path.parts:
            item.add_marker(pytest.mark.integration)
            item.add_marker(pytest.mark.slow)
