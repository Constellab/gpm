"""Brick package installation and discovery from community service."""

import os
import shutil

from .community_service import CommunityBrick, CommunityService
from .config_reader import SettingsReader
from .git_package_installer import GitPackageInstaller
from .logger import Logger
from .workspace_config import WorkspaceConfig


class BrickInstaller:
    """Handles brick package installation from community service.

    This class manages:
    - Brick installation from community service
    - Brick discovery and prioritization (user vs system)
    - Recursive brick dependency installation
    - Brick validation
    """

    def __init__(
        self,
        workspace_config: WorkspaceConfig,
        git_installer: GitPackageInstaller,
        community_service: CommunityService,
        logger: Logger,
    ):
        """Initialize the brick installer.

        Args:
            workspace_config: Workspace configuration for paths
            git_installer: Git package installer for cloning bricks
            community_service: Community service for fetching brick metadata
            logger: Logger instance for logging operations
        """
        self.workspace_config = workspace_config
        self.git_installer = git_installer
        self.community_service = community_service
        self.logger = logger
        self._installed_bricks: list[str] = []

    def install_brick(self, name: str, version: str, parent_name: str) -> SettingsReader:
        """Install a single brick from the community service.

        Bricks are installed to the .sys/bricks folder. If a brick with the same name
        exists in user/bricks, it takes priority for dependencies.

        Args:
            name: Name of the brick to install
            version: Version of the brick to install
            parent_name: Name of the parent brick that requires this brick

        Returns:
            SettingsReader for the installed brick (prioritizes user folder if exists)
        """
        brick_info: CommunityBrick = self.community_service.get_brick(name, version)

        repo_path = brick_info["repositoryAccessUrl"]

        # Path of the brick in sys and user folder
        sys_brick_dir = os.path.join(self.workspace_config.sys_bricks_folder, name)
        user_brick_dir = os.path.join(self.workspace_config.user_bricks_folder, name)

        # Remove brick in sys folder if it exists, then install
        if os.path.exists(sys_brick_dir):
            self.logger.info(f"Removing {sys_brick_dir} ...")
            try:
                shutil.rmtree(sys_brick_dir)
            except Exception as err:
                raise Exception(f"Cannot remove {sys_brick_dir}") from err

        # Install the brick in sys folder
        self.logger.info(
            f"Cloning brick '{name}' version '{version}' from {brick_info['repositoryUrl']}."
        )
        self.git_installer.git_clone(
            url=repo_path,
            dest_dir=sys_brick_dir,
            repo_name=name,
            parent_name=parent_name,
            version=version,
        )

        # Check if the brick is installed
        if not os.path.exists(sys_brick_dir):
            error = f"Brick package {name} version {version} could not be installed."
            # If the brick exists in user folder, only log the error
            if os.path.exists(user_brick_dir):
                self.logger.error(
                    f"Brick '{name}' version '{version}' is already installed in the user bricks folder."
                )
            else:
                raise Exception(error)

        # Mark as installed
        self._installed_bricks.append(name)

        # For the rest, use brick in user dir if it exists (user override)
        brick_dir = user_brick_dir if os.path.exists(user_brick_dir) else sys_brick_dir

        # Return the settings reader for sub-dependency installation
        return SettingsReader(os.path.join(brick_dir, self.workspace_config.SETTING_JSON_FILE))

    def _install_sub_brick(
        self, settings_readers: list[SettingsReader]
    ) -> list[SettingsReader]:
        """Install brick packages from settings readers and collect sub-dependencies.

        Args:
            settings_readers: List of SettingsReader instances containing brick package configurations

        Returns:
            List of SettingsReader instances for sub-dependencies
        """
        sub_settings_readers: list[SettingsReader] = []

        for settings_reader in settings_readers:
            self.logger.info(f"Installing bricks for '{settings_reader.get_name()}' brick")

            # Get all the brick packages
            for brick in settings_reader.get_brick_packages():
                if self.is_installed(brick["name"]):
                    continue

                # Install the brick
                sub_reader = self.install_brick(
                    name=brick["name"],
                    version=brick["version"],
                    parent_name=settings_reader.get_name(),
                )
                sub_settings_readers.append(sub_reader)

        return sub_settings_readers

    def list_all_brick_paths(self) -> dict[str, str]:
        """Return a dictionary of all bricks from user and sys folders.

        User bricks take priority over sys bricks - if a brick exists in both locations,
        only the user version is included in the result.

        Returns:
            Dictionary where key is brick_name and value is brick_path
        """
        user_bricks = self.get_bricks_in_folder(self.workspace_config.user_bricks_folder)
        sys_bricks = self.get_bricks_in_folder(self.workspace_config.sys_bricks_folder)

        # Add sys bricks that don't exist in user bricks
        for brick_name, brick_path in sys_bricks.items():
            if brick_name not in user_bricks:
                user_bricks[brick_name] = brick_path

        return user_bricks

    def get_bricks_in_folder(self, path: str) -> dict[str, str]:
        """Return a dictionary of all bricks found in the specified folder.

        Args:
            path: Path to the folder to search for bricks

        Returns:
            Dictionary where key is brick_name and value is brick_path
        """
        brick_paths = {}
        for brick_folder in os.listdir(path):
            brick_path = os.path.join(path, brick_folder)
            # Only process directories
            if os.path.isdir(brick_path) and self.folder_is_brick(brick_path):
                brick_paths[brick_folder] = brick_path
        return brick_paths

    def folder_is_brick(self, path: str) -> bool:
        """Check if a folder is a valid brick.

        A folder is considered a brick if it contains both:
        - A settings.json file
        - A src folder

        Args:
            path: Path to the folder to check

        Returns:
            True if the folder is a valid brick, False otherwise
        """
        return os.path.exists(
            os.path.join(path, self.workspace_config.SETTING_JSON_FILE)
        ) and os.path.exists(os.path.join(path, self.workspace_config.SOURCE_FOLDER))

    def is_installed(self, brick_name: str) -> bool:
        """Check if a brick is already installed.

        Args:
            brick_name: Name of the brick to check

        Returns:
            True if the brick is installed, False otherwise
        """
        return brick_name in self._installed_bricks

    def get_installed_bricks(self) -> list[str]:
        """Get list of all installed bricks.

        Returns:
            Sorted list of installed brick names
        """
        bricks = self._installed_bricks.copy()
        bricks.sort()
        return bricks

    def install_git_packages_and_bricks(self, settings_readers: list[SettingsReader]) -> None:
        """Recursively install git packages and bricks from settings readers.

        This method clones git repositories and brick packages. It does NOT collect or install
        pip dependencies - that is handled separately by collect_and_install_pip_dependencies().

        Sub-packages are installed after main packages to maintain proper dependency order.

        Args:
            settings_readers: List of SettingsReader instances containing package configurations
        """
        # Install git packages (no pip dependencies collected here)
        for settings_reader in settings_readers:
            self.logger.info(f"Installing git packages for '{settings_reader.get_name()}' brick")
            self.git_installer.install_git_packages(settings_reader)

        # Install bricks recursively
        sub_settings_readers = self._install_sub_brick(settings_readers)

        # Recursive call to install sub-packages
        if len(sub_settings_readers) > 0:
            self.install_git_packages_and_bricks(sub_settings_readers)
