"""Unit tests for BrickInstaller failure tracking and sys-folder pruning.

These tests mock the community service, git installer, and filesystem interactions
that BrickInstaller depends on, so they run without network or git.
"""

import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from init.script.brick_installer import BrickInstaller
from init.script.workspace_config import WorkspaceConfig


@pytest.fixture
def workspace(tmp_path: Path) -> WorkspaceConfig:
    """A WorkspaceConfig pointing at a temp lab dir with all folders created."""
    config = WorkspaceConfig(
        lab_workspace_dir=str(tmp_path),
        data_folder=str(tmp_path / "data"),
    )
    config.initialize_directories()
    return config


@pytest.fixture
def installer(workspace: WorkspaceConfig) -> BrickInstaller:
    """A BrickInstaller with mocked git installer and community service."""
    git_installer = MagicMock()
    community_service = MagicMock()
    logger = MagicMock()
    return BrickInstaller(workspace, git_installer, community_service, logger)


def _make_brick_dir(workspace: WorkspaceConfig, name: str) -> str:
    """Materialize a brick folder structure that folder_is_brick() accepts."""
    brick_dir = os.path.join(workspace.sys_bricks_folder, name)
    os.makedirs(os.path.join(brick_dir, workspace.SOURCE_FOLDER), exist_ok=True)
    # Minimal valid settings.json so SettingsReader won't blow up if reached
    with open(
        os.path.join(brick_dir, workspace.SETTING_JSON_FILE), "w", encoding="utf-8"
    ) as f:
        f.write('{"name": "' + name + '"}')
    return brick_dir


def _make_reader(name: str, brick_deps=None, git_packages=None):
    """Build a SettingsReader-like mock returning a fixed set of dependencies."""
    reader = MagicMock()
    reader.get_name.return_value = name
    reader.get_brick_packages.return_value = brick_deps or []
    reader.get_git_packages.return_value = git_packages or []
    reader.get_environment_variables.return_value = {}
    return reader


class TestFailureTracking:
    """Failed brick names are captured so they can be surfaced to the caller."""

    def test_successful_walk_records_no_failures(self, installer: BrickInstaller):
        reader = _make_reader("app", brick_deps=[])

        installer.install_git_packages_and_bricks([reader])

        assert installer.get_failed_bricks() == []

    def test_failed_brick_is_recorded_by_name(self, installer: BrickInstaller):
        reader = _make_reader(
            "app", brick_deps=[{"name": "brick_a", "version": "1.0"}]
        )
        installer.community_service.get_brick.side_effect = Exception("community down")

        installer.install_git_packages_and_bricks([reader])

        assert installer.get_failed_bricks() == ["brick_a"]

    def test_sibling_bricks_still_attempted_after_failure(
        self, installer: BrickInstaller
    ):
        """A failing brick must not stop later sibling bricks from being tried."""
        reader = _make_reader(
            "app",
            brick_deps=[
                {"name": "brick_a", "version": "1.0"},
                {"name": "brick_b", "version": "1.0"},
            ],
        )

        # brick_a fails; brick_b succeeds (returns a minimal CommunityBrick)
        def get_brick_side_effect(name, version):
            if name == "brick_a":
                raise Exception("community down for brick_a")
            return {
                "brickName": name,
                "brickVersion": version,
                "repoType": "git",
                "repositoryUrl": "https://example.com/b.git",
                "repositoryAccessUrl": "https://example.com/b.git",
            }

        installer.community_service.get_brick.side_effect = get_brick_side_effect

        # Make git_clone materialize brick_b's folder so install_brick's post-clone
        # path check succeeds, and returns a reader with no sub-deps.
        def clone_side_effect(url, dest_dir, repo_name, parent_name, version):
            os.makedirs(os.path.join(dest_dir, "src"), exist_ok=True)
            with open(
                os.path.join(dest_dir, "settings.json"), "w", encoding="utf-8"
            ) as f:
                f.write('{"name": "' + repo_name + '"}')

        installer.git_installer.git_clone.side_effect = clone_side_effect

        installer.install_git_packages_and_bricks([reader])

        assert installer.get_failed_bricks() == ["brick_a"]
        assert "brick_b" in installer.get_installed_bricks()

    def test_git_package_failure_is_tagged_to_parent(
        self, installer: BrickInstaller
    ):
        reader = _make_reader("parent_brick", git_packages=[MagicMock()])
        installer.git_installer.install_git_packages.side_effect = Exception("boom")

        installer.install_git_packages_and_bricks([reader])

        failures = installer.get_failed_bricks()
        assert len(failures) == 1
        assert "parent_brick" in failures[0]


class TestPruneGating:
    """Prune only runs when the walk completed without failures."""

    def test_prune_removes_unvisited_bricks_on_success(
        self, installer: BrickInstaller, workspace: WorkspaceConfig
    ):
        # Two bricks exist on disk; only one was "visited" this run
        _make_brick_dir(workspace, "kept_brick")
        orphan_dir = _make_brick_dir(workspace, "orphan_brick")
        installer._installed_bricks = ["kept_brick"]

        installer.prune_sys_bricks()

        assert os.path.exists(
            os.path.join(workspace.sys_bricks_folder, "kept_brick")
        )
        assert not os.path.exists(orphan_dir)

    def test_prune_is_skipped_when_any_brick_failed(
        self, installer: BrickInstaller, workspace: WorkspaceConfig
    ):
        """Partial walk → orphan must survive, because it might be a sub-dep we
        never reached (parent resolution failed)."""
        _make_brick_dir(workspace, "kept_brick")
        orphan_dir = _make_brick_dir(workspace, "orphan_brick")
        installer._installed_bricks = ["kept_brick"]
        installer._failed_bricks = ["some_failed_brick"]

        installer.prune_sys_bricks()

        assert os.path.exists(orphan_dir), (
            "orphan must survive a failed walk — it could be a legitimate sub-dep"
        )

    def test_prune_ignores_non_directory_entries(
        self, installer: BrickInstaller, workspace: WorkspaceConfig
    ):
        """Stray files in sys_bricks_folder must not confuse pruning."""
        _make_brick_dir(workspace, "kept_brick")
        stray_file = os.path.join(workspace.sys_bricks_folder, "stray.txt")
        with open(stray_file, "w", encoding="utf-8") as f:
            f.write("not a brick")
        installer._installed_bricks = ["kept_brick"]

        installer.prune_sys_bricks()

        assert os.path.exists(stray_file)
