"""Main orchestrator for package management operations."""

import json
import os
from typing import Literal

from .brick_installer import BrickInstaller
from .community_service import CommunityService
from .config_reader import SettingsReader
from .git_package_installer import GitPackageInstaller
from .hook_executor import HookExecutor
from .logger import Logger
from .pip_manager import PipManager
from .url_formatter import UrlFormatter
from .workspace_config import WorkspaceConfig

EnvMode = Literal["GLAB", "CODELAB"]


class GencoveryPackageManager:
    """Main orchestrator for package management operations.

    This is a facade that coordinates all package management operations by delegating
    to specialized components. It maintains the high-level installation workflow.
    """

    INSTALL_DEPENDENCIES_PROGRESS_START: float = 10.0
    INSTALL_DEPENDENCIES_PROGRESS_END: float = 90.0

    def __init__(
        self,
        settings_file_path: str,
        env_mode: str,
        workspace_config: WorkspaceConfig,
    ):
        """Initialize the package manager with all components.

        Args:
            settings_file_path: Path to the main settings.json file
            env_mode: Environment mode (GLAB or CODELAB)
            workspace_config: Workspace configuration (built from env via
                ``WorkspaceConfig.from_env()`` in production)

        Raises:
            Exception: If env_mode is invalid or None
        """
        # Validate environment mode
        if env_mode is None:
            raise Exception("Please specify the environment mode (--env-mode)")

        if env_mode not in {"GLAB", "CODELAB"}:
            raise Exception(f"Environment mode must be either GLAB or CODELAB, not '{env_mode}'")

        self.env_mode = env_mode
        self.settings_file_path = settings_file_path

        # Initialize workspace configuration
        self.workspace_config = workspace_config
        self.workspace_config.initialize_directories()

        # Initialize logger
        self.logger = Logger(self.workspace_config.get_start_log_file_path())
        self.logger.info(
            f"Initializing GPM with env mode: {env_mode} using settings file: {settings_file_path}"
        )

        # Initialize config reader
        self.config_reader = SettingsReader(self.settings_file_path)

        # Initialize URL formatter
        self.url_formatter = UrlFormatter(self.config_reader)

        # Initialize git package installer
        self.git_installer = GitPackageInstaller(
            self.workspace_config, self.logger, self.url_formatter
        )

        # Initialize brick installer
        self.brick_installer = BrickInstaller(
            self.workspace_config,
            self.git_installer,
            CommunityService(),
            self.logger,
        )

        # Initialize pip manager
        self.pip_manager = PipManager(
            self.logger,
            self.INSTALL_DEPENDENCIES_PROGRESS_START,
            self.INSTALL_DEPENDENCIES_PROGRESS_END,
        )

        # Initialize hook executor
        self.hook_executor = HookExecutor(self.logger)

    def init_all(self):
        """Initialize the lab environment by installing all packages, dependencies, and running hooks.

        This is the main entry point that orchestrates the full installation process:
        1. Install git packages and bricks recursively
        2. Collect and install pip dependencies from all bricks
        3. Configure settings.json for the app
        4. Execute post-install hooks
        """
        self.logger.info("[Starting lab]")
        self.logger.log_progress("Installing bricks", 0)

        # Step 1: Install all git packages and bricks recursively. Individual brick
        # failures are logged and swallowed by the installer so sibling bricks still
        # get a chance. We only raise afterwards, and only in GLAB mode.
        try:
            self.brick_installer.install_git_packages_and_bricks([self.config_reader])

            git_packages = self.git_installer.get_installed_packages()
            self.logger.info(f"Installed git packages:\n{git_packages}")

            brick_packages = self.brick_installer.get_installed_bricks()
            self.logger.info(f"Installed brick packages:\n{brick_packages}")

            # Prune only if every brick installed cleanly — a partial walk would
            # wrongly delete still-needed sub-dependencies we never reached.
            try:
                self.brick_installer.prune_sys_bricks()
            except Exception as prune_err:
                self.logger.error(f"Error while pruning sys bricks. {prune_err}")

            failed_bricks = self.brick_installer.get_failed_bricks()
            if failed_bricks:
                msg = (
                    f"{len(failed_bricks)} brick(s) failed to install: "
                    f"{', '.join(failed_bricks)}"
                )
                self.logger.main_error(msg)
                if self.env_mode == "GLAB":
                    raise Exception(msg)
        except Exception as err:
            self.logger.main_error(f"Error while installing git packages and bricks. {err}")
            # In codelab, ignore the error so it starts even if packages are not installed
            if self.env_mode == "GLAB":
                raise err

        self.logger.log_progress(
            "Installing bricks dependencies", self.INSTALL_DEPENDENCIES_PROGRESS_START
        )

        # Step 2: Collect and install pip dependencies from all installed bricks
        try:
            self.collect_and_install_pip_dependencies()
        except Exception as err:
            self.logger.main_error(f"Error while installing pip packages. {err}")
            # In codelab, ignore the error so it starts even if packages are not installed
            if self.env_mode == "GLAB":
                raise err

        self.logger.log_progress("Starting lab", self.INSTALL_DEPENDENCIES_PROGRESS_END)

        # Step 3: Configure settings.json
        self.configure_settings_json()

        # Step 4: Execute post-install hooks
        self.logger.info("Calling brick hooks...")
        try:
            self.call_brick_hooks()
        except Exception as err:
            self.logger.error(f"Error while calling brick hooks. {err}")
            # Don't fail the initialization if hooks fail

    def collect_and_install_pip_dependencies(self) -> None:
        """Collect pip dependencies from all installed bricks and install them.

        Prioritizes bricks in user folder over .sys folder.
        """
        self.logger.info("Collecting pip dependencies from all installed bricks...")

        # Get all bricks from both user and sys folders
        all_bricks = self.brick_installer.list_all_brick_paths()

        self.logger.info(f"Found {len(all_bricks)} bricks to process for dependencies")

        # Collect pip packages from each brick
        for brick_name, brick_path in all_bricks.items():
            settings_file = os.path.join(brick_path, self.workspace_config.SETTING_JSON_FILE)

            if not os.path.exists(settings_file):
                self.logger.error(
                    f"Settings file not found for brick '{brick_name}' at {settings_file}"
                )
                continue

            try:
                brick_reader = SettingsReader(settings_file)
                pip_packages = brick_reader.get_pip_packages()

                if pip_packages:
                    self.logger.info(
                        f"Adding {len(pip_packages)} pip packages from brick '{brick_name}' (from {brick_path})"
                    )
                    self.pip_manager.add_packages(pip_packages, brick_name)
                else:
                    self.logger.info(f"No pip packages found for brick '{brick_name}'")
            except Exception as err:
                self.logger.error(f"Error reading settings for brick '{brick_name}': {err}")
                # Continue with other bricks even if one fails
                continue

        # Install all collected pip packages
        self.logger.info("Installing all collected pip dependencies...")
        self.pip_manager.install_packages()

    def configure_settings_json(self):
        """Create settings.json file containing the main config info for the app entrypoint."""
        try:
            settings_file = self.workspace_config.get_app_settings_file_path()
            self.logger.info(f"Generating settings.json file at {settings_file} ...")

            settings = {
                "name": self.config_reader.get_name(),
                "version": "1.0.0",
                "variables": self.config_reader.get_variables(),
                "environment": self.config_reader.get_environment(),
            }
            with open(settings_file, "w", encoding="utf-8") as file:
                json.dump(settings, file, indent=4)

        except Exception as err:
            self.logger.main_error(f"Error while creating the app entrypoint: {err}")
            raise err

    def call_brick_hooks(self) -> None:
        """Call post-install hooks for all installed bricks."""
        self.hook_executor.execute_hooks_for_bricks(
            self.workspace_config.user_bricks_folder,
            self.workspace_config.sys_bricks_folder,
        )
