# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import json
import os
import re
import shutil
import time
from datetime import datetime
from typing import Dict, List, Literal, Optional, TypedDict

from git import Repo

from .community_service import CommunityBrick, CommunityService
from .config_reader import SettingsReader
from .logger import Logger
from .package_lock import PackageLock
from .pip_manager import PipManager

# ####################################################################
#
# GPM class
#
# ####################################################################
EnvMode = Literal['GLAB', 'CODELAB']


class BrickInstalationInfo(TypedDict):
    """ Use to create a file in the cloned repository to have information about the brick installation """
    name: str
    version: str
    parent_name: str
    git_hash: Optional[str]
    package_type: Literal["pip", "git"]
    path: str
    created_at: str


class GPM():
    """
    Package manager
    """
    LAB_WORKSPACE_DIR: str = "/lab"
    SYS_WORKSPACE_DIR: str = None
    USER_WORKSPACE_DIR: str = None

    USER_BRICKS_FOLDER: str = None
    NOTEBOOK_FOLDER: str = None
    SYS_BRICKS_FOLDER: str = None
    APP_BRICK_FOLDER: str = None
    EXTERNAL_LIB_FOLDER: str = None
    USER_DATA_FOLDER: str = None

    CONFIG_FILE_PATH: str = "/conf/config.json"
    SETTING_JSON_FILE: str = "settings.json"
    GIT_INSTALLATION_FILE = ".gws-git-installation.json"

    SOURCE_FOLDER: str = 'src'
    # path where the default config for vs code is stored (it need to be copied to the user workspace)
    VS_CODE_DEFAULT_CONFIG_PATH = "/.vs-code-server-config"

    config_reader: SettingsReader = None
    package_lock: PackageLock

    pip_manager: PipManager = None

    _installed_pip_packages: list = []
    _installed_git_packages: list = []
    _installed_brick_packages: list = []

    env_mode: EnvMode = None

    def __init__(self, settings_file_path: str, env_mode: EnvMode):
        self.SYS_WORKSPACE_DIR: str = os.path.join(
            self.LAB_WORKSPACE_DIR, '.sys')
        self.USER_WORKSPACE_DIR: str = os.path.join(
            self.LAB_WORKSPACE_DIR, 'user')

        self.USER_BRICKS_FOLDER = os.path.join(
            self.USER_WORKSPACE_DIR, 'bricks')
        self.NOTEBOOK_FOLDER = os.path.join(
            self.USER_WORKSPACE_DIR, "notebooks")
        self.USER_DATA_FOLDER = os.path.join(self.USER_WORKSPACE_DIR, 'data')
        self.SYS_BRICKS_FOLDER = os.path.join(self.SYS_WORKSPACE_DIR, 'bricks')
        self.APP_BRICK_FOLDER = os.path.join(self.SYS_WORKSPACE_DIR, 'app')
        self.EXTERNAL_LIB_FOLDER = os.path.join(self.SYS_WORKSPACE_DIR, 'lib')

        self.create_folder_if_not_exists(self.SYS_WORKSPACE_DIR)
        self.create_folder_if_not_exists(self.USER_WORKSPACE_DIR)
        self.create_folder_if_not_exists(self.USER_BRICKS_FOLDER)
        self.create_folder_if_not_exists(self.USER_DATA_FOLDER)
        self.create_folder_if_not_exists(self.NOTEBOOK_FOLDER)
        self.create_folder_if_not_exists(self.SYS_BRICKS_FOLDER)
        self.create_folder_if_not_exists(self.APP_BRICK_FOLDER)
        self.create_folder_if_not_exists(self.EXTERNAL_LIB_FOLDER)

        Logger.info(f"Initializing GPM with env mode: {env_mode} using settings file: {settings_file_path}")
        self.settings_file_path = settings_file_path

        # Check that the env mode is valid GLAB or CODELAB
        if env_mode is None:
            raise Exception("Please specify the environment mode (--env-mode)")

        if env_mode != 'GLAB' and env_mode != 'CODELAB':
            raise Exception(
                f"Environment mode must be either GLAB or CODELAB, not '{env_mode}'")

        self.env_mode = env_mode

        self.pip_manager = PipManager()
        self._installed_git_packages: list = []
        self._installed_brick_packages: list = []

        self.config_reader = SettingsReader(self.settings_file_path)
        self.package_lock = PackageLock()

    def init_all(self):

        try:
            self.install_git_packages_and_bricks([self.config_reader])

            git_packages = self._installed_git_packages
            git_packages.sort()
            Logger.info(f"Installed git packages:\n{git_packages}")
        except Exception as err:
            Logger.error(f"Error while installing git packages: {err}")
            raise err

        try:
            # install all the pip packages
            self.pip_manager.install_packages()
        except Exception as err:
            # in codelab, ignore the error so it start the CODELAB
            # even if packages are no installed
            if self.env_mode == 'GLAB':
                raise err

        self.configure_settings_json()
        self.configure_vscode()

    def install_git_packages_and_bricks(self, settings_readers: List[SettingsReader]) -> None:
        """Recursive method to install pip and git packages. The sub packages are installed after the main packages.

        :param settings_readers: _description_
        :type settings_readers: List[SettingsReader]
        """

        # install git and pip packages
        for settings_reader in settings_readers:
            Logger.info(
                f"Installing git packages for '{settings_reader.get_name()}' brick")
            self._install_git_packages(settings_reader)

            # store the pip packages to install them later
            self.pip_manager.add_packages(settings_reader.get_pip_packages())

        # install bricks
        self.install_bricks(settings_readers)

    def _install_git_packages(self, settings_reader: SettingsReader) -> None:

        parent_name = settings_reader.get_name()
        for package in settings_reader.get_git_packages():

            repo_name = package["name"]
            # skip install if the package is already installed
            if repo_name in self._installed_git_packages:
                continue

            version = package.get("version", "")
            source_url = package.get("source").strip("/")
            repo_path = f"{source_url}/{repo_name}.git"
            Logger.info(f"Cloning git repository '{repo_path}:{version}' ... ")

            # replace the variable name with the values (including credentials)
            repo_path = self.format_url(
                repo_path, settings_reader.get_environment_variables())

            # install the package
            self._install_git_package(
                repo_name, version, repo_path, parent_name)

            self._installed_git_packages.append(repo_name)

    def _install_git_package(self, repo_name: str, version: str, repo_path: str, parent_name: str) -> None:

        repo_dir = os.path.join(self.EXTERNAL_LIB_FOLDER, repo_name)

        if os.path.exists(repo_dir):
            Logger.info(f"Removing '{repo_dir}'")
            try:
                shutil.rmtree(repo_dir)
            except:
                raise Exception(f"Cannot remove '{repo_dir}'")
        self.git_clone(url=repo_path, dest_dir=repo_dir,
                       repo_name=repo_name, parent_name=parent_name, version=version)

        if not os.path.exists(repo_dir):
            raise Exception(
                f"Git package '{repo_name}' version '{version}' could not be installed.")

    def install_bricks(self, settings_readers: List[SettingsReader]) -> None:
        sub_settings_readers: List[SettingsReader] = []

        for settings_reader in settings_readers:
            Logger.info(
                f"Installing bricks dependencies for '{settings_reader.get_name()}' brick")

            # get all the bricks packages
            for brick in settings_reader.get_brick_packages():
                if brick['name'] in self._installed_brick_packages:
                    continue

                # install the brick
                sub_reader = self.install_brick(name=brick.get("name"),
                                                version=brick.get("version"),
                                                parent_name=settings_reader.get_name())
                sub_settings_readers.append(sub_reader)

        # recursive call to install sub packages
        # the sub packages are install after the main packages
        if len(sub_settings_readers) > 0:
            self.install_git_packages_and_bricks(sub_settings_readers)

    def install_brick(self, name: str, version: str,
                      parent_name: str) -> SettingsReader:

        brick_info: CommunityBrick = CommunityService().get_brick(name, version)

        repo_path = brick_info["repositoryAccessUrl"]

        # path of the brick in sys and user folder
        sys_brick_dir = os.path.join(self.SYS_BRICKS_FOLDER, name)
        user_brick_dir = os.path.join(self.USER_BRICKS_FOLDER, name)

        # remove brick in sys folder
        if os.path.exists(sys_brick_dir):
            Logger.info(f"Removing {sys_brick_dir} ...")
            try:
                shutil.rmtree(sys_brick_dir)
            except:
                raise Exception(f"Cannot remove {sys_brick_dir}")

        # install the brick in sys folder
        if not os.path.exists(sys_brick_dir):
            Logger.info(
                f"Cloning brick '{name}' version '{version}' from {brick_info['repositoryUrl']}.")
            self.git_clone(url=repo_path, dest_dir=sys_brick_dir,
                           repo_name=name, parent_name=parent_name, version=version)

        # check if the brick is installed
        if not os.path.exists(sys_brick_dir):
            error = f"Brick package {name} version {version} could not be installed."
            # if the brick exists in user folder, only log the error
            if os.path.exists(user_brick_dir):
                Logger.error(
                    f"Brick '{name}' version '{version}' is already installed in the user bricks folder.")
            else:
                raise Exception(error)

        self._installed_brick_packages.append(name)

        # for the rest, use brick in user dir if it exists
        brick_dir = user_brick_dir if os.path.exists(
            user_brick_dir) else sys_brick_dir

        # return the sub settings so the sub dependencies can be installed
        return SettingsReader(os.path.join(brick_dir, self.SETTING_JSON_FILE))

    def git_clone(self, url: str, dest_dir: str, repo_name: str, parent_name: str, version: str = None) -> None:
        # Try to clone the repository 3 times if it fails
        repo: Repo
        nb_retry = 0
        while True:
            try:
                if version:
                    repo = Repo.clone_from(
                        url=url, to_path=dest_dir, branch=version, depth=1)
                else:
                    repo = Repo.clone_from(url=url, to_path=dest_dir, depth=1)
                break
            except Exception as err:
                Logger.info(
                    f"Couldn't clone the repository '{repo_name}' with version '{version}'. Error: {err}")
                Logger.info("Waiting 3 secs and retry ...")
                time.sleep(3)
                nb_retry += 1
                if nb_retry >= 3:
                    raise err

        self.create_git_installation_file(name=repo_name, path=dest_dir, parent_name=parent_name,
                                          git_hash=repo.head.object.hexsha, version=version)

        # remove .git folder
        try:
            shutil.rmtree(os.path.join(dest_dir, ".git"))
        except:
            raise Exception(f"Cannot remove .git directory from {dest_dir}")

    def configure_settings_json(self):
        """Create settings.json file containing the main config info for the app entrypoint
        """
        try:

            # Really important, update the settings.json file with main config info so the bricks will be loaded on start
            settings_file = os.path.join(
                self.APP_BRICK_FOLDER, self.SETTING_JSON_FILE)
            Logger.info(f"Generating settings.json file at {settings_file} ...")

            settings = {
                "name": self.config_reader.get_name(),
                "version": "1.0.0",
                "variables": self.config_reader.get_variables(),
                "environment": self.config_reader.get_environment()
            }
            with open(settings_file, 'w', encoding='utf-8') as file:
                json.dump(settings, file, indent=4)

        except Exception as err:
            Logger.error(f"Error while creating the app entrypoint: {err}")
            raise err

    def format_url(self, string: str, variables: Dict[str, str]) -> str:
        if not string:
            return string

        if not variables:
            variables = {}

        global_config_vars = self.config_reader.get_environment_variables()

        # re.findall(r"\${?[A-Z_]}?*", string)
        tab = re.findall(r"\$\{?([A-Z_]*)\}?", string)
        for token in tab:
            # search for values in local variable first
            value = variables.get(token)
            if not value:
                # search for values in os environment
                value = os.getenv(token)
                if not value:
                    # search for values in global environment (given by the main config file)
                    value = global_config_vars.get(token)
                    if not value:
                        raise Exception(
                            f"No environment variable {token} found")

            if value:
                string = re.sub(r"\$\{?"+token+r"\}?", value, string)

        return string

    def list_all_brick_paths(self) -> Dict[str, str]:
        """ return a list of all the bricks in the user and sys folder
        Where key = brick_name and value = brick_path"""

        user_bricks = self.get_bricks_in_folder(self.USER_BRICKS_FOLDER)
        sys_bricks = self.get_bricks_in_folder(self.SYS_BRICKS_FOLDER)

        for brick_name, brick_path in sys_bricks.items():
            if brick_name not in user_bricks:
                user_bricks[brick_name] = brick_path
        return user_bricks

    def get_bricks_in_folder(self, path: str) -> Dict[str, str]:
        """return a list of all the bricks in the provided folder
        """
        brick_paths: {} = {}
        for brick_folder in os.listdir(path):
            brick_path = os.path.join(path, brick_folder)
            if self.folder_is_brick(brick_path):
                brick_paths[brick_folder] = brick_path
        return brick_paths

    def folder_is_brick(self, path: str) -> bool:
        """return true if the provided folder is a brick.
        If the folder contains a settings.json and a src folder it is a brick

        """
        return os.path.exists(os.path.join(path, self.SETTING_JSON_FILE)) and \
            os.path.exists(os.path.join(path, self.SOURCE_FOLDER))

    def create_folder_if_not_exists(self, path: str) -> None:
        if not os.path.exists(path):
            os.makedirs(path)

    def configure_vscode(self) -> None:
        if self.env_mode != 'CODELAB':
            return

        Logger.info("Configuring VS Code ...")

        vs_code_folder = self.get_vs_code_setting_folder()
        if not os.path.exists(vs_code_folder):
            os.mkdir(vs_code_folder)

        # always override the extensions.json file
        extensions_dest = os.path.join(vs_code_folder, 'extensions.json')
        shutil.copyfile(os.path.join(self.VS_CODE_DEFAULT_CONFIG_PATH, 'extensions.json'),
                        extensions_dest)
        # always override the launch.json file
        shutil.copyfile(os.path.join(self.VS_CODE_DEFAULT_CONFIG_PATH, 'launch.json'),
                        os.path.join(vs_code_folder, 'launch.json'))

        # copy the pylint files
        shutil.copyfile(os.path.join(self.VS_CODE_DEFAULT_CONFIG_PATH, '.pylintrc'),
                        os.path.join(self.USER_WORKSPACE_DIR, '.pylintrc'))
        shutil.copyfile(os.path.join(self.VS_CODE_DEFAULT_CONFIG_PATH, '.mypy.ini'),
                        os.path.join(self.USER_WORKSPACE_DIR, '.mypy.ini'))
        shutil.copyfile(os.path.join(self.VS_CODE_DEFAULT_CONFIG_PATH, 'pylint_init.py'),
                        os.path.join(self.USER_WORKSPACE_DIR, 'pylint_init.py'))

        self._config_vs_code_settings_json()
        self.install_notebook_template()
        self._install_vscode_extensions(extensions_dest)
        Logger.info("VS Code configured !")

    def _config_vs_code_settings_json(self) -> None:
        """Configure the vscode settings.json file to add the bricks to the python path
        """
        Logger.info("Configuring VS Code settings.json file")
        settings_path = self.get_vs_code_settings_file_path()

        # load the settings file into a dict
        settings: dict = None
        if not os.path.exists(settings_path):
            Logger.info('Creating a new vscode settings file')
            settings = self._generate_vs_code_settings_json(settings_path)
        else:
            Logger.info('Reading the existing vscode settings file')
            try:
                with open(settings_path, 'r', encoding='UTF-8') as file:
                    settings = json.load(file)
            except Exception as err:
                Logger.error(f"Error during parsing of the vscode settings file : {err}.")
                Logger.error("Moving the existing file to settings_backup.json and creating a new one ...")
                shutil.move(settings_path, os.path.join(self.get_vs_code_setting_folder(), "settings_backup.json"))
                # create a new settings file
                settings = self._generate_vs_code_settings_json(settings_path)
                return

        Logger.info("Adding the bricks to the python path ...")
        # init the extra paths if not already done
        if 'python.autoComplete.extraPaths' not in settings \
                or not isinstance(settings['python.autoComplete.extraPaths'], list):
            settings['python.autoComplete.extraPaths'] = []

        # add the brick paths to the extra paths
        existing_paths: List[str] = settings['python.autoComplete.extraPaths']

        # set all the brick src paths in the extraPaths
        brick_infos = self.list_all_brick_paths()
        new_paths: List[str] = [os.path.join(brick_path, self.SOURCE_FOLDER) for brick_path in brick_infos.values()]

        # add the existing path that are not brick path (added manually by the user)
        for existing_path in existing_paths:
            found = False
            for brick_name in brick_infos.keys():
                if brick_name in existing_path:
                    found = True
                    break
            if not found:
                new_paths.append(existing_path)
        settings['python.autoComplete.extraPaths'] = new_paths

        try:
            Logger.info('Writting the vscode settings file ...')
            # write the settings file
            with open(settings_path, 'w', encoding='UTF-8') as file:
                json.dump(settings, file, indent=2)
        except Exception as err:
            Logger.error(
                f"Error during writting the vscode settings file : {err}")
            return

    def _generate_vs_code_settings_json(self, settings_path: str) -> dict:
        # copy the settings.json file only if it does not exist
        shutil.copyfile(os.path.join(self.VS_CODE_DEFAULT_CONFIG_PATH, 'settings.json'), settings_path)

        # load the settings file into a dict
        with open(settings_path, 'r', encoding='UTF-8') as file:
            return json.load(file)

    def _install_vscode_extensions(self, extension_file_path: str) -> None:
        """Install the vscode extensions
        """
        Logger.info("Installing vscode extensions ...")
        # load the settings file into a dict
        extensions: dict = None
        with open(extension_file_path, 'r', encoding='UTF-8') as file:
            extensions = json.load(file)

        # install the extensions
        for extension in extensions["recommendations"]:
            Logger.info(f"Installing extension {extension} ...")
            os.system(f"/home/.openvscode-server/bin/openvscode-server code --install-extension {extension}")

    def install_notebook_template(self):

        Logger.info("Installing notebook template ...")

        __cdir__ = os.path.dirname(os.path.abspath(__file__))
        src_notebook_dir = os.path.abspath(
            os.path.join(__cdir__, '..', "notebook_template"))

        tempalate_dir = os.path.join(self.NOTEBOOK_FOLDER, "template")
        if os.path.exists(tempalate_dir):
            # override only the env.py file
            Logger.info(f"Updating {tempalate_dir} ...")
            shutil.copyfile(
                os.path.join(src_notebook_dir, "env.py"),
                os.path.join(tempalate_dir, "env.py")
            )

        else:
            shutil.copytree(src_notebook_dir, tempalate_dir)

    def get_vs_code_setting_folder(self) -> str:
        return os.path.join(self.USER_WORKSPACE_DIR, ".vscode")

    def get_vs_code_settings_file_path(self) -> str:
        return os.path.join(self.get_vs_code_setting_folder(), "settings.json")

    def create_git_installation_file(self, name: str, path: str, parent_name: str,
                                     git_hash: str, version: str = None) -> None:
        """Create a file in the git repo directory containing the git installation info for logging purpose
        """

        brick_installation: BrickInstalationInfo = {
            "name": name,
            "version": version,
            "parent_name": parent_name,
            "git_hash": git_hash,
            "path": path,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        git_installation_file = os.path.join(path, self.GIT_INSTALLATION_FILE)
        with open(git_installation_file, 'w', encoding='UTF-8') as file:
            json.dump(brick_installation, file, indent=2)
