"""Workspace configuration and directory management for the lab environment."""

import os


class WorkspaceConfig:
    """Manages lab workspace directory structure and paths.

    This class is responsible for defining and initializing all workspace directories
    used by the package manager. It provides a centralized configuration for paths
    and ensures all required directories exist.
    """

    LAB_WORKSPACE_DIR: str = "/lab"
    SETTING_JSON_FILE: str = "settings.json"
    SOURCE_FOLDER: str = "src"
    GIT_INSTALLATION_FILE: str = ".gws-git-installation.json"
    CONFIG_FILE_PATH: str = "/conf/config.json"

    def __init__(self, lab_workspace_dir: str = "/lab"):
        """Initialize workspace configuration with all directory paths.

        Args:
            lab_workspace_dir: Root directory for the lab workspace (default: /lab)
        """
        self.LAB_WORKSPACE_DIR = lab_workspace_dir

        # Main workspace directories
        self.sys_workspace_dir = os.path.join(self.LAB_WORKSPACE_DIR, ".sys")
        self.user_workspace_dir = os.path.join(self.LAB_WORKSPACE_DIR, "user")

        # User workspace subdirectories
        self.user_bricks_folder = os.path.join(self.user_workspace_dir, "bricks")
        self.notebook_folder = os.path.join(self.user_workspace_dir, "notebooks")
        self.user_data_folder = os.path.join(self.user_workspace_dir, "data")

        # System workspace subdirectories
        self.sys_bricks_folder = os.path.join(self.sys_workspace_dir, "bricks")
        self.app_brick_folder = os.path.join(self.sys_workspace_dir, "app")
        self.external_lib_folder = os.path.join(self.sys_workspace_dir, "lib")

    def initialize_directories(self) -> None:
        """Create all required workspace directories if they don't exist."""
        self.create_folder_if_not_exists(self.sys_workspace_dir)
        self.create_folder_if_not_exists(self.user_workspace_dir)
        self.create_folder_if_not_exists(self.user_bricks_folder)
        self.create_folder_if_not_exists(self.user_data_folder)
        self.create_folder_if_not_exists(self.notebook_folder)
        self.create_folder_if_not_exists(self.sys_bricks_folder)
        self.create_folder_if_not_exists(self.app_brick_folder)
        self.create_folder_if_not_exists(self.external_lib_folder)

    def create_folder_if_not_exists(self, path: str) -> None:
        """Create a folder and all parent directories if they don't exist.

        Args:
            path: Path to the folder to create
        """
        if not os.path.exists(path):
            os.makedirs(path)

    def get_start_log_file_path(self) -> str:
        """Get the path to the start log file.

        Returns:
            Full path to the start-log.json file
        """
        return os.path.join(self.sys_workspace_dir, "start-log.json")

    def get_app_settings_file_path(self) -> str:
        """Get the path to the app settings.json file.

        Returns:
            Full path to the app settings.json file
        """
        return os.path.join(self.app_brick_folder, self.SETTING_JSON_FILE)
