"""Git package installation with retry logic and metadata tracking."""

import json
import os
import shutil
import time
from datetime import datetime
from typing import Literal, TypedDict

from git import GitCommandError, Repo

from .config_reader import SettingsReader
from .logger import Logger
from .url_formatter import UrlFormatter
from .workspace_config import WorkspaceConfig


class BrickInstallationInfo(TypedDict):
    """Metadata for tracking git package installations."""

    name: str
    version: str | None
    parent_name: str
    git_hash: str | None
    package_type: Literal["pip", "git"]
    path: str
    created_at: str


class GitPackageInstaller:
    """Handles git repository cloning and package installation.

    This class manages:
    - Git package installation from settings
    - Git cloning with retry logic
    - Installation metadata tracking
    - Package deduplication
    """

    MAX_RETRIES: int = 3
    RETRY_DELAY_SECONDS: int = 3

    def __init__(
        self,
        workspace_config: WorkspaceConfig,
        logger: Logger,
        url_formatter: UrlFormatter,
    ):
        """Initialize the git package installer.

        Args:
            workspace_config: Workspace configuration for paths
            logger: Logger instance for logging operations
            url_formatter: URL formatter for credential substitution
        """
        self.workspace_config = workspace_config
        self.logger = logger
        self.url_formatter = url_formatter
        self._installed_packages: list[str] = []

    def install_git_packages(self, settings_reader: SettingsReader) -> None:
        """Install all git packages defined in a settings reader.

        Args:
            settings_reader: SettingsReader instance containing git package configurations
        """
        parent_name = settings_reader.get_name()
        for package in settings_reader.get_git_packages():
            repo_name = package.name

            # Skip install if the package is already installed
            if self.is_installed(repo_name):
                continue

            version: str | None = package.version or None
            source_url = (package.source or "").strip("/")
            repo_path = f"{source_url}/{repo_name}.git"

            # Replace environment variables (including credentials)
            repo_path = self.url_formatter.format_url(
                repo_path, settings_reader.get_environment_variables()
            )

            # Log without exposing credentials
            safe_repo_path = self.url_formatter.redact_credentials(repo_path)
            self.logger.info(
                f"Cloning git repository '{repo_name}' from '{safe_repo_path}' version '{version}' ... "
            )

            # Install the package
            self.install_git_package(repo_name, version, repo_path, parent_name)

            # Mark as installed
            self._installed_packages.append(repo_name)

    def install_git_package(
        self, repo_name: str, version: str | None, repo_path: str, parent_name: str
    ) -> None:
        """Install a single git package by cloning it to the external lib folder.

        Args:
            repo_name: Name of the repository
            version: Git branch/tag to clone, or None for default branch
            repo_path: Full URL path to the git repository
            parent_name: Name of the parent brick that requires this package
        """
        repo_dir = os.path.join(self.workspace_config.external_lib_folder, repo_name)

        # Remove existing directory if it exists
        if os.path.exists(repo_dir):
            self.logger.info(f"Removing '{repo_dir}'")
            try:
                shutil.rmtree(repo_dir)
            except Exception as err:
                raise Exception(f"Cannot remove '{repo_dir}'") from err

        # Clone the repository
        self.git_clone(
            url=repo_path,
            dest_dir=repo_dir,
            repo_name=repo_name,
            parent_name=parent_name,
            version=version,
        )

        # Verify installation
        if not os.path.exists(repo_dir):
            raise Exception(
                f"Git package '{repo_name}' version '{version}' could not be installed."
            )

    def git_clone(
        self,
        url: str,
        dest_dir: str,
        repo_name: str,
        parent_name: str,
        version: str | None = None,
    ) -> None:
        """Clone a git repository with retry logic.

        Attempts to clone the repository up to MAX_RETRIES times with delays between attempts.
        Creates a git installation file with metadata and removes the .git folder after cloning.

        Args:
            url: Git repository URL to clone from
            dest_dir: Destination directory for the cloned repository
            repo_name: Name of the repository
            parent_name: Name of the parent brick that requires this repository
            version: Git branch/tag to clone, or None for default branch

        Raises:
            Exception: If cloning fails after MAX_RETRIES attempts or if .git directory cannot be removed
        """
        repo: Repo
        retry_count = 0

        while True:
            try:
                if version:
                    repo = Repo.clone_from(url=url, to_path=dest_dir, branch=version, depth=1)
                else:
                    repo = Repo.clone_from(url=url, to_path=dest_dir, depth=1)
                break
            except GitCommandError as err:
                # Check if the error is due to a missing tag/branch
                error_message = str(err)
                if version and (
                    "Remote branch" in error_message
                    and "not found" in error_message
                    or "couldn't find remote ref" in error_message.lower()
                    or "does not exist" in error_message.lower()
                ):
                    raise Exception(
                        f"Tag or branch '{version}' does not exist in repository '{repo_name}'. "
                        f"Please verify the version (tag) exists in the repository."
                    ) from err

                # For other git errors, retry
                self.logger.info(
                    f"Couldn't clone the repository '{repo_name}' with version '{version}'. Error: {err}"
                )
                self.logger.info(f"Waiting {self.RETRY_DELAY_SECONDS} secs and retry ...")
                time.sleep(self.RETRY_DELAY_SECONDS)
                retry_count += 1
                if retry_count >= self.MAX_RETRIES:
                    raise err
            except Exception as err:
                # For non-git errors, retry
                self.logger.info(
                    f"Couldn't clone the repository '{repo_name}' with version '{version}'. Error: {err}"
                )
                self.logger.info(f"Waiting {self.RETRY_DELAY_SECONDS} secs and retry ...")
                time.sleep(self.RETRY_DELAY_SECONDS)
                retry_count += 1
                if retry_count >= self.MAX_RETRIES:
                    raise err

        # Create installation metadata file
        self.create_git_installation_file(
            name=repo_name,
            path=dest_dir,
            parent_name=parent_name,
            git_hash=repo.head.object.hexsha,
            version=version,
        )

        # Remove .git folder to save space
        try:
            shutil.rmtree(os.path.join(dest_dir, ".git"))
        except Exception as err:
            raise Exception(f"Cannot remove .git directory from {dest_dir}") from err

    def create_git_installation_file(
        self, name: str, path: str, parent_name: str, git_hash: str, version: str | None = None
    ) -> None:
        """Create a metadata file in the git repo directory with installation information.

        This file is used for logging and tracking purposes.

        Args:
            name: Name of the repository/package
            path: Path where the repository was installed
            parent_name: Name of the parent brick that required this package
            git_hash: Git commit hash of the cloned version
            version: Git branch/tag that was cloned, or None for default branch
        """
        brick_installation: BrickInstallationInfo = {
            "name": name,
            "version": version,
            "parent_name": parent_name,
            "git_hash": git_hash,
            "path": path,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "package_type": "git",
        }

        git_installation_file = os.path.join(path, self.workspace_config.GIT_INSTALLATION_FILE)
        with open(git_installation_file, "w", encoding="UTF-8") as file:
            json.dump(brick_installation, file, indent=2)

    def is_installed(self, repo_name: str) -> bool:
        """Check if a git package is already installed.

        Args:
            repo_name: Name of the repository to check

        Returns:
            True if the package is installed, False otherwise
        """
        return repo_name in self._installed_packages

    def get_installed_packages(self) -> list[str]:
        """Get list of all installed git packages.

        Returns:
            Sorted list of installed package names
        """
        packages = self._installed_packages.copy()
        packages.sort()
        return packages
