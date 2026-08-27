"""Unit tests for GPM (Gencovery Package Manager).

These tests run the real install path — bricks are really cloned, dependencies
really resolved — against a local git registry instead of the community API
(see tests/fixtures/local_brick_registry.py). That keeps them offline: no
network, no COMMUNITY_API_URL, no SPACE_API_KEY. Only the `git` binary is
needed, hence the requires_git marker.
"""

import json
import os
import shutil
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from init.script.config_reader import SettingsReader
from init.script.gencovery_package_manager import GencoveryPackageManager
from init.script.git_package_installer import BrickInstallationInfo
from init.script.workspace_config import WorkspaceConfig
from tests.fixtures.local_brick_registry import LocalBrickRegistry

GWS_CORE_VERSION = "0.8.0"
# Must match the brick requested by tests/fixtures/config.json — the registry
# fixture asserts this, so a change to that file fails loudly here.
GWS_BIOTA_VERSION = "0.7.0"
BIOTA_PIP_PACKAGE = "pronto"


@pytest.fixture
def test_workspace(tmp_path):
    """Create a clean lab workspace for testing."""
    workspace = tmp_path / "lab"
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace


@pytest.fixture
def config_path():
    """Get the path to the test configuration file."""
    return Path(__file__).parent.parent / "fixtures" / "config.json"


@pytest.fixture
def brick_registry(tmp_path, config_path) -> LocalBrickRegistry:
    """A local stand-in for the community API, holding the bricks config.json asks for.

    Mirrors the real dependency shape: the app requires gws_biota, which pulls
    gws_core as a sub-brick, one external git package, and one pip package.
    """
    requested = {
        brick["name"]: brick["version"]
        for brick in SettingsReader(str(config_path)).get_brick_packages()
    }
    assert requested == {"gws_biota": GWS_BIOTA_VERSION}, (
        "tests/fixtures/config.json no longer matches the bricks this registry provides"
    )

    registry = LocalBrickRegistry(str(tmp_path / "registry"))

    # External (non-brick) git package, cloned into the lib folder.
    registry.add_repo("brendapy", files={"README.md": "# brendapy\n"})

    registry.add_brick("gws_core", GWS_CORE_VERSION)
    registry.add_brick(
        "gws_biota",
        GWS_BIOTA_VERSION,
        brick_deps=[{"name": "gws_core", "version": GWS_CORE_VERSION}],
        git_channels=[{"source": registry.source_url, "packages": [{"name": "brendapy"}]}],
        pip_channels=[
            {
                "source": "https://pypi.python.org/simple",
                "packages": [{"name": BIOTA_PIP_PACKAGE}],
            }
        ],
    )
    return registry


@pytest.fixture
def gpm_factory(test_workspace, config_path, tmp_path, brick_registry, monkeypatch):
    """Build a GPM wired to the local registry, with pip installs stubbed out.

    Collecting a brick's pip dependencies is asserted below; actually running
    `pip install` would need PyPI, and is covered by test_pip_manager.
    """

    def make_gpm(env_mode: str) -> GencoveryPackageManager:
        gpm = GencoveryPackageManager(
            settings_file_path=str(config_path),
            env_mode=env_mode,
            workspace_config=WorkspaceConfig(
                lab_workspace_dir=str(test_workspace),
                data_folder=str(tmp_path / "data"),
            ),
            community_service=brick_registry.community_service,
        )
        monkeypatch.setattr(gpm.pip_manager, "install_packages", MagicMock())
        return gpm

    return make_gpm


@pytest.fixture
def gpm_instance(gpm_factory) -> GencoveryPackageManager:
    """Create a GPM instance for testing."""
    return gpm_factory("GLAB")


class TestGpmGlab:
    """Tests for GPM in GLAB mode."""

    @pytest.mark.requires_git
    def test_glab_initialization(self, gpm_instance: GencoveryPackageManager):
        """Test that GPM initializes correctly in GLAB mode."""
        # Initialize all packages
        gpm_instance.init_all()

        # Check that gws_core was cloned (as a sub-dependency of gws_biota)
        gws_core_brick_path = os.path.join(
            gpm_instance.workspace_config.sys_bricks_folder, "gws_core"
        )
        gws_core_settings_path = os.path.join(gws_core_brick_path, "settings.json")
        assert os.path.exists(gws_core_settings_path)

        # Check that gws_biota was cloned
        gws_biota_brick_path = os.path.join(
            gpm_instance.workspace_config.sys_bricks_folder, "gws_biota"
        )
        gws_biota_settings_path = os.path.join(gws_biota_brick_path, "settings.json")
        assert os.path.exists(gws_biota_settings_path)

        # Check that brendapy was cloned
        brendapy_readme_path = os.path.join(
            gpm_instance.workspace_config.external_lib_folder, "brendapy", "README.md"
        )
        assert os.path.exists(brendapy_readme_path)

        # The clone is a plain folder, not a working git repo
        assert not os.path.exists(os.path.join(gws_core_brick_path, ".git"))

    @pytest.mark.requires_git
    def test_pip_dependencies_are_collected_from_bricks(
        self, gpm_instance: GencoveryPackageManager
    ):
        """Test that pip dependencies declared by a brick reach the pip manager."""
        gpm_instance.init_all()

        collected = {(pkg.name, pkg.brick_name) for pkg in gpm_instance.pip_manager.packages}
        assert (BIOTA_PIP_PACKAGE, "gws_biota") in collected
        gpm_instance.pip_manager.install_packages.assert_called_once()

    @pytest.mark.requires_git
    def test_brick_installation_info(self, gpm_instance: GencoveryPackageManager):
        """Test that brick installation information is properly recorded."""
        gpm_instance.init_all()

        gws_core_brick_path = os.path.join(
            gpm_instance.workspace_config.sys_bricks_folder, "gws_core"
        )
        info_file_path = os.path.join(
            gws_core_brick_path, gpm_instance.workspace_config.GIT_INSTALLATION_FILE
        )

        assert os.path.exists(info_file_path)

        with open(info_file_path) as f:
            info: BrickInstallationInfo = json.load(f)
            assert info["version"] == GWS_CORE_VERSION
            assert info["name"] == "gws_core"
            # Check that gws_core was installed because of gws_biota dependency
            assert info["parent_name"] == "gws_biota"
            assert len(info["git_hash"]) > 0
            assert len(info["created_at"]) > 0

    @pytest.mark.requires_git
    def test_brick_update(self, gpm_instance: GencoveryPackageManager):
        """Test that brick update works correctly."""
        gpm_instance.init_all()

        gws_core_brick_path = os.path.join(
            gpm_instance.workspace_config.sys_bricks_folder, "gws_core"
        )

        # Delete the README file to test update
        readme = os.path.join(gws_core_brick_path, "README.md")
        os.remove(readme)
        assert not os.path.exists(readme)

        # Re-install the brick
        gpm_instance.brick_installer.install_brick("gws_core", GWS_CORE_VERSION, "app")

        # README should be restored
        assert os.path.exists(readme)

    @pytest.mark.requires_git
    def test_unknown_brick_version_fails_the_install(
        self, gpm_instance: GencoveryPackageManager
    ):
        """A brick the registry cannot resolve is reported as a failure, not silently skipped."""
        with pytest.raises(Exception, match="not found in local registry"):
            gpm_instance.brick_installer.install_brick("gws_core", "99.0.0", "app")

    @pytest.mark.requires_git
    def test_list_brick_paths(self, gpm_instance: GencoveryPackageManager):
        """Test listing all brick paths."""
        gpm_instance.init_all()

        brick_paths = gpm_instance.brick_installer.list_all_brick_paths()

        assert set(brick_paths) == {"gws_core", "gws_biota"}

        gws_core_brick_path = os.path.join(
            gpm_instance.workspace_config.sys_bricks_folder, "gws_core"
        )
        gws_biota_brick_path = os.path.join(
            gpm_instance.workspace_config.sys_bricks_folder, "gws_biota"
        )

        assert gws_core_brick_path in brick_paths.values()
        assert gws_biota_brick_path in brick_paths.values()

    @pytest.mark.requires_git
    def test_app_start_configuration(self, gpm_instance: GencoveryPackageManager):
        """Test that app start is properly configured."""
        gpm_instance.init_all()

        sys_app_path = os.path.join(gpm_instance.workspace_config.sys_workspace_dir, "app")

        assert os.path.exists(sys_app_path)
        assert os.path.exists(os.path.join(sys_app_path, "settings.json"))

        setting_reader = SettingsReader(os.path.join(sys_app_path, "settings.json"))

        # Check that gws_biota is listed
        packages = setting_reader.get_brick_packages()
        biota_packages = [x for x in packages if x["name"] == "gws_biota"]
        assert len(biota_packages) == 1


class TestGpmCodelab:
    """Tests for GPM in CODELAB mode."""

    @pytest.mark.requires_git
    def test_codelab_initialization(self, gpm_factory):
        """Test that GPM initializes correctly in CODELAB mode."""
        gpm = gpm_factory("CODELAB")
        gpm.init_all()

        # Test moving brick to non-hidden folder
        gws_core_path = os.path.join(gpm.workspace_config.sys_bricks_folder, "gws_core")
        gws_core_dest_path = os.path.join(gpm.workspace_config.user_bricks_folder, "gws_core")

        shutil.move(gws_core_path, gws_core_dest_path)

        # Delete the README file to test update behavior
        readme = os.path.join(gws_core_dest_path, "README.md")
        os.remove(readme)
        assert not os.path.exists(readme)

        # Re-install gws_core - it should not update since it's in user brick folder
        gpm.brick_installer.install_brick("gws_core", GWS_CORE_VERSION, "app")
        assert not os.path.exists(readme)
