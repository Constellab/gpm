"""Unit tests for GPM (Gencovery Package Manager)."""

import importlib
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from init.script.config_reader import SettingsReader
from init.script.gencovery_package_manager import GencoveryPackageManager
from init.script.git_package_installer import BrickInstallationInfo

GWS_CORE_VERSION = "0.8.0"


@pytest.fixture
def test_workspace(tmp_path):
    """Create a temporary workspace for testing."""
    workspace = tmp_path / "lab"
    workspace.mkdir()
    return workspace


@pytest.fixture
def config_path():
    """Get the path to the test configuration file."""
    return Path(__file__).parent.parent / "fixtures" / "config.json"


@pytest.fixture
def gpm_instance(test_workspace, config_path):
    """Create a GPM instance for testing."""
    return GencoveryPackageManager(
        settings_file_path=str(config_path),
        env_mode="GLAB",
        lab_workspace_dir=str(test_workspace),
    )


class TestGpmGlab:
    """Tests for GPM in GLAB mode."""

    @pytest.mark.slow
    @pytest.mark.requires_network
    @pytest.mark.requires_git
    def test_glab_initialization(self, gpm_instance: GencoveryPackageManager):
        """Test that GPM initializes correctly in GLAB mode."""
        # Uninstall pronto to test fresh installation
        subprocess.run(["pip", "uninstall", "pronto", "-y"], check=False)

        # Check that pronto is not installed
        assert importlib.find_loader("pronto") is None

        # Initialize all packages
        gpm_instance.init_all()

        # Check that gws_core was cloned
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

        # Check that pip dependencies of biota are installed
        assert importlib.find_loader("pronto") is not None

    @pytest.mark.slow
    @pytest.mark.requires_network
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

    @pytest.mark.slow
    @pytest.mark.requires_network
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

    @pytest.mark.slow
    @pytest.mark.requires_network
    @pytest.mark.requires_git
    def test_list_brick_paths(self, gpm_instance: GencoveryPackageManager):
        """Test listing all brick paths."""
        gpm_instance.init_all()

        brick_paths = gpm_instance.brick_installer.list_all_brick_paths()

        assert len(brick_paths) == 2

        gws_core_brick_path = os.path.join(
            gpm_instance.workspace_config.sys_bricks_folder, "gws_core"
        )
        gws_biota_brick_path = os.path.join(
            gpm_instance.workspace_config.sys_bricks_folder, "gws_biota"
        )

        assert gws_core_brick_path in brick_paths.values()
        assert gws_biota_brick_path in brick_paths.values()

    @pytest.mark.slow
    @pytest.mark.requires_network
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

    @pytest.mark.slow
    @pytest.mark.requires_network
    @pytest.mark.requires_git
    def test_codelab_initialization(self, test_workspace, config_path):
        """Test that GPM initializes correctly in CODELAB mode."""
        gpm = GencoveryPackageManager(
            settings_file_path=str(config_path),
            env_mode="CODELAB",
            lab_workspace_dir=str(test_workspace),
        )
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
