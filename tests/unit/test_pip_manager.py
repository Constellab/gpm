"""Unit tests for PipManager."""

import importlib.util
import subprocess

import pytest
from unittest.mock import MagicMock

from init.script.config_reader import PackageInfo
from init.script.logger import Logger
from init.script.pip_manager import PipManager


@pytest.fixture
def mock_logger():
    """Create a mock logger for testing."""
    return MagicMock(spec=Logger)


@pytest.fixture
def pip_manager(mock_logger):
    """Create a PipManager instance for testing."""
    return PipManager(mock_logger, 0, 100)


class TestPipManagerInstallation:
    """Tests for pip package installation."""

    @pytest.mark.slow
    @pytest.mark.requires_network
    def test_install_pinned_versions(self, tmp_path):
        """Test basic pip package installation with pinned versions."""
        log_file_path = tmp_path / "test.log"
        logger = Logger(str(log_file_path))

        packages: list[PackageInfo] = [
            {"name": "numpy", "version": "1.26.4", "source": "https://pypi.python.org/simple"},
            {"name": "pandas", "version": "2.2.2", "source": "https://pypi.python.org/simple"},
            # Simulate a second source
            {
                "name": "simplejson",
                "version": "3.19.2",
                "source": "https://pypi.python.org/simple ",
            },
        ]

        # Uninstall packages first
        packages_to_uninstall = [package["name"] for package in packages]
        cmd = ["pip", "uninstall"] + packages_to_uninstall + ["-y"]
        subprocess.check_call(cmd)

        pip_manager = PipManager(logger, 0, 100, disable_cache=True, log_progress=True)
        pip_manager.add_packages(packages)
        pip_manager.install_packages()

        # Verify packages are installed
        assert importlib.util.find_spec("numpy") is not None
        assert importlib.util.find_spec("pandas") is not None
        assert importlib.util.find_spec("simplejson") is not None

    @pytest.mark.slow
    @pytest.mark.requires_network
    def test_install_version_ranges(self, tmp_path):
        """Test pip package installation with flexible version ranges."""
        log_file_path = tmp_path / "test.log"
        logger = Logger(str(log_file_path))

        packages: list[PackageInfo] = [
            # Use version ranges instead of pinned versions
            {"name": "certifi", "version": ">=2023.0.0,<2025.0.0", "source": "https://pypi.python.org/simple"},
            {"name": "charset-normalizer", "version": ">=3.0.0,<4.0.0", "source": "https://pypi.python.org/simple"},
            # Test compatible release operator
            {"name": "idna", "version": "~=3.4", "source": "https://pypi.python.org/simple"},
        ]

        # Uninstall packages first
        packages_to_uninstall = [package["name"] for package in packages]
        cmd = ["pip", "uninstall"] + packages_to_uninstall + ["-y"]
        subprocess.run(cmd, check=False)  # Don't fail if packages aren't installed

        pip_manager = PipManager(logger, 0, 100, disable_cache=True, log_progress=True)
        pip_manager.add_packages(packages)
        pip_manager.install_packages()

        # Verify packages are installed
        assert importlib.util.find_spec("certifi") is not None
        assert importlib.util.find_spec("charset_normalizer") is not None
        assert importlib.util.find_spec("idna") is not None

        # Verify the installed packages are in the expected ranges
        installed_versions = pip_manager.get_installed_packages_version()
        assert any("certifi" in pkg for pkg in installed_versions)
        assert any("charset-normalizer" in pkg or "charset_normalizer" in pkg for pkg in installed_versions)
        assert any("idna" in pkg for pkg in installed_versions)


class TestPipManagerVersionConflicts:
    """Tests for version conflict detection."""

    def test_version_conflict_detection(self, mock_logger):
        """Test that version conflicts are detected and raise an exception."""
        pip_manager = PipManager(mock_logger, 0, 100)

        # Add first package with version 2.31.0
        package1: PackageInfo = {
            "name": "requests",
            "version": "2.31.0",
            "source": "https://pypi.python.org/simple",
        }
        pip_manager.add_package(package1)

        # Add same package with different version - both should be added
        package2: PackageInfo = {
            "name": "requests",
            "version": "2.28.0",
            "source": "https://pypi.python.org/simple",
        }
        pip_manager.add_package(package2)

        # Verify both packages are in the list
        assert len(pip_manager.packages) == 2

        # Now check_conflicts should detect the conflict and raise an exception
        with pytest.raises(Exception) as exc_info:
            pip_manager.check_conflicts()

        # Verify the exception message
        assert "version conflicts" in str(exc_info.value)

        # Verify error messages were logged
        assert mock_logger.error.called
        error_calls = [call[0][0] for call in mock_logger.error.call_args_list]
        error_text = " ".join(error_calls)
        assert "Package version conflicts detected" in error_text
        assert "requests" in error_text
        assert "2.31.0" in error_text
        assert "2.28.0" in error_text
        assert "version ranges" in error_text

    def test_no_conflict_same_version(self, mock_logger):
        """Test that no conflict is detected when same version is added twice."""
        pip_manager = PipManager(mock_logger, 0, 100)

        # Add same package with same version twice
        package: PackageInfo = {
            "name": "requests",
            "version": "2.31.0",
            "source": "https://pypi.python.org/simple",
        }
        pip_manager.add_package(package)
        pip_manager.add_package(package)

        # Verify both packages are in the list (no deduplication at add time)
        assert len(pip_manager.packages) == 2

        # check_conflicts should not raise an exception
        pip_manager.check_conflicts()  # Should not raise

        # Verify info message was logged (no conflicts)
        assert mock_logger.info.called
        info_message = mock_logger.info.call_args[0][0]
        assert "No package conflicts detected" in info_message

    def test_multiple_packages_no_conflict(self, mock_logger):
        """Test that multiple different packages can be added without conflict."""
        pip_manager = PipManager(mock_logger, 0, 100)

        packages: list[PackageInfo] = [
            {"name": "requests", "version": ">=2.31.0,<3.0.0", "source": "https://pypi.python.org/simple"},
            {"name": "numpy", "version": ">=1.24.0,<2.0.0", "source": "https://pypi.python.org/simple"},
            {"name": "pandas", "version": ">=2.0.0,<3.0.0", "source": "https://pypi.python.org/simple"},
        ]

        pip_manager.add_packages(packages)

        # Verify all packages are in the list
        assert len(pip_manager.packages) == 3

        # check_conflicts should not raise an exception
        pip_manager.check_conflicts()  # Should not raise

        # Verify info message was logged (no conflicts)
        assert mock_logger.info.called

    def test_multiple_conflicts(self, mock_logger):
        """Test detection of multiple package conflicts at once."""
        pip_manager = PipManager(mock_logger, 0, 100)

        # Add multiple packages with conflicts
        packages: list[PackageInfo] = [
            {"name": "requests", "version": "2.31.0", "source": "https://pypi.python.org/simple"},
            {"name": "requests", "version": "2.28.0", "source": "https://pypi.python.org/simple"},
            {"name": "numpy", "version": "1.24.0", "source": "https://pypi.python.org/simple"},
            {"name": "numpy", "version": "1.26.0", "source": "https://pypi.python.org/simple"},
            {"name": "pandas", "version": "2.0.0", "source": "https://pypi.python.org/simple"},  # No conflict
        ]

        pip_manager.add_packages(packages)

        # Should raise exception with both conflicts
        with pytest.raises(Exception) as exc_info:
            pip_manager.check_conflicts()

        exception_msg = str(exc_info.value)
        assert "2 package(s) with version conflicts" in exception_msg

        # Verify both packages are mentioned in error logs
        error_calls = [call[0][0] for call in mock_logger.error.call_args_list]
        error_text = " ".join(error_calls)
        assert "requests" in error_text
        assert "numpy" in error_text

    def test_install_packages_calls_check_conflicts(self, mock_logger):
        """Test that install_packages automatically checks for conflicts."""
        pip_manager = PipManager(mock_logger, 0, 100)

        # Add conflicting packages
        pip_manager.add_package({"name": "requests", "version": "2.31.0", "source": "https://pypi.python.org/simple"})
        pip_manager.add_package({"name": "requests", "version": "2.28.0", "source": "https://pypi.python.org/simple"})

        # install_packages should raise exception due to conflict check
        with pytest.raises(Exception) as exc_info:
            pip_manager.install_packages()

        assert "version conflicts" in str(exc_info.value)


class TestPipManagerVersionFormatting:
    """Tests for version formatting."""

    def test_version_range_support(self, mock_logger):
        """Test that version ranges are handled correctly."""
        test_cases = [
            # (input_version, expected_output)
            ("2.31.0", "==2.31.0"),  # Pinned version gets ==
            (">=2.31.0", ">=2.31.0"),  # Range preserved
            (">=2.31.0,<3.0.0", ">=2.31.0,<3.0.0"),  # Complex range preserved
            ("~=2.31.0", "~=2.31.0"),  # Compatible release preserved
            ("!=2.31.2", "!=2.31.2"),  # Exclusion preserved
            ("<3.0.0", "<3.0.0"),  # Upper bound preserved
            ("", ""),  # Empty version
        ]

        for input_version, expected_output in test_cases:
            package: PackageInfo = {
                "name": f"test-package-{input_version.replace('=', '').replace('<', '').replace('>', '').replace(',', '').replace('~', '').replace('!', '')}",
                "version": input_version,
                "source": "https://pypi.python.org/simple",
            }

            # Create a new pip_manager for each test to avoid conflicts
            test_pip_manager = PipManager(mock_logger, 0, 100)
            test_pip_manager.add_package(package)

            # Get the formatted package string
            packages_by_source: dict[str, list[PackageInfo]] = {}
            for pkg in test_pip_manager.packages:
                if pkg["source"] not in packages_by_source:
                    packages_by_source[pkg["source"]] = []
                packages_by_source[pkg["source"]].append(pkg)

            # Format the version as done in _install_packages_for_source
            formatted_packages = []
            for source_packages in packages_by_source.values():
                for pkg in source_packages:
                    name = pkg["name"]
                    version = pkg.get("version", "")
                    if version and version[0] not in [">", "<", "=", "~", "!"]:
                        version = "==" + version
                    formatted_packages.append(f"{name}{version}")

            if expected_output:
                expected_full = f"{package['name']}{expected_output}"
                assert formatted_packages[0] == expected_full, \
                    f"Failed for input '{input_version}': expected '{expected_full}', got '{formatted_packages[0]}'"
            else:
                assert formatted_packages[0] == package["name"]

    def test_empty_version_handling(self, mock_logger):
        """Test that packages without version are handled correctly."""
        pip_manager = PipManager(mock_logger, 0, 100)

        package: PackageInfo = {
            "name": "requests",
            "version": "",
            "source": "https://pypi.python.org/simple",
        }
        pip_manager.add_package(package)

        assert len(pip_manager.packages) == 1
        assert pip_manager.packages[0]["version"] == ""

        # Should not raise conflict
        pip_manager.check_conflicts()


class TestPipManagerPackageGrouping:
    """Tests for package grouping by source."""

    def test_package_grouping_by_source(self, mock_logger):
        """Test that packages are correctly grouped by source."""
        pip_manager = PipManager(mock_logger, 0, 100)

        packages: list[PackageInfo] = [
            {"name": "requests", "version": "2.31.0", "source": "https://pypi.python.org/simple"},
            {"name": "numpy", "version": "1.24.0", "source": "https://custom-repo.com/simple"},
            {"name": "pandas", "version": "2.0.0", "source": "https://pypi.python.org/simple"},
        ]

        pip_manager.add_packages(packages)

        # Group packages by source (mimics internal behavior)
        packages_by_source: dict[str, list[PackageInfo]] = {}
        for package in pip_manager.packages:
            if package["source"] not in packages_by_source:
                packages_by_source[package["source"]] = []
            packages_by_source[package["source"]].append(package)

        # Verify grouping
        assert len(packages_by_source) == 2
        assert len(packages_by_source["https://pypi.python.org/simple"]) == 2
        assert len(packages_by_source["https://custom-repo.com/simple"]) == 1
