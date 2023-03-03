# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import json
import os
import re
import shutil
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Literal, Optional, TypedDict

from git import Repo

from .config_reader import GitPackage, SettingsReader
from .package_lock import PackageLock

# ####################################################################
#
# GPM class
#
# ####################################################################
EnvMode = Literal['GLAB', 'CODELAB']


class ClonedPackage(TypedDict):
    version: Optional[str]
    git_hash: str
    name: str
    path: str


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
    NOTEBOOK_FOLDER : str = None
    SYS_BRICKS_FOLDER: str = None
    APP_BRICK_FOLDER: str = None
    EXTERNAL_LIB_FOLDER: str = None
    
    CONFIG_FILE_PATH: str = "/conf/config.json"
    SETTING_JSON_FILE: str = "settings.json"
    BRICK_INSTALLATION_FILE = ".brick-installation.json"

    SOURCE_FOLDER: str = 'src'
    # path where the default config for vs code is stored (it need to be copied to the user workspace)
    VS_CODE_DEFAULT_CONFIG_PATH = "/.vs-code-server-config"

    config_reader: SettingsReader = None
    package_lock: PackageLock

    _installed_pip_packages: list = []
    _installed_git_packages: list = []

    env_mode: EnvMode = None

    def __init__(self, settings_file_path: str, env_mode: EnvMode):
        self.SYS_WORKSPACE_DIR: str = os.path.join(self.LAB_WORKSPACE_DIR, '.sys')
        self.USER_WORKSPACE_DIR: str = os.path.join(self.LAB_WORKSPACE_DIR, 'user')

        self.USER_BRICKS_FOLDER = os.path.join(self.USER_WORKSPACE_DIR, 'bricks')
        self.NOTEBOOK_FOLDER = os.path.join(self.USER_WORKSPACE_DIR, "notebooks")
        self.SYS_BRICKS_FOLDER = os.path.join(self.SYS_WORKSPACE_DIR, 'bricks')
        self.APP_BRICK_FOLDER = os.path.join(self.SYS_WORKSPACE_DIR, 'app')
        self.EXTERNAL_LIB_FOLDER = os.path.join(self.SYS_WORKSPACE_DIR, 'lib')
        
        self.create_folder_if_not_exists(self.SYS_WORKSPACE_DIR)
        self.create_folder_if_not_exists(self.USER_WORKSPACE_DIR)
        self.create_folder_if_not_exists(self.USER_BRICKS_FOLDER)
        self.create_folder_if_not_exists(self.NOTEBOOK_FOLDER)
        self.create_folder_if_not_exists(self.SYS_BRICKS_FOLDER)
        self.create_folder_if_not_exists(self.APP_BRICK_FOLDER)
        self.create_folder_if_not_exists(self.EXTERNAL_LIB_FOLDER)

        print(f"Initializing GPM with env mode: {env_mode}")
        self.settings_file_path = settings_file_path

        # Check that the env mode is valid GLAB or CODELAB
        if env_mode is None:
            raise Exception("Please specify the environment mode (--env-mode)")

        if env_mode != 'GLAB' and env_mode != 'CODELAB':
            raise Exception(f"Environment mode must be either GLAB or CODELAB, not '{env_mode}'")

        self.env_mode = env_mode
        self._installed_pip_packages: list = []
        self._installed_git_packages: list = []

        self.config_reader = SettingsReader(self.settings_file_path)
        self.package_lock = PackageLock()

    def init_all(self):
        self.install_pip_and_git_packages([self.config_reader])
        self.install_app_entrypoint()
        # install notbook here and not in dockerfile because it is in the volumes
        self.install_notebook_entrypoint()
        self.configure_vscode()

    def install_pip_and_git_packages(self, settings_readers: List[SettingsReader]) -> None:
        """Recursive method to install pip and git packages. The sub packages are installed after the main packages.

        :param settings_readers: _description_
        :type settings_readers: List[SettingsReader]
        """

        sub_settings_readers: List[SettingsReader] = []
        for settings_reader in settings_readers:
            print(f"Installing Pip and Git packages for brick {settings_reader.get_name()}")
            for pip_chanel in settings_reader.get_pip_channels():
                self._install_pip_packages(pip_chanel.get("packages"), source_url=pip_chanel.get("source"),
                                           env_variables=settings_reader.get_environment_variables())

            sub_reader = self.install_git_packages(settings_reader)
            sub_settings_readers.extend(sub_reader)

        # recursive call to install sub packages
        # the sub packages are install after the main packages
        if len(sub_settings_readers) > 0:
            self.install_pip_and_git_packages(sub_settings_readers)

    def _install_pip_packages(self, packages: list, source_url=None, env_variables: Dict[str, str] = None):
        if len(packages) == 0:
            return

        # format the source url by remplacing the env variables
        source_url = self.format_url(source_url, env_variables)

        _packages: List[str] = []
        _repos: List[str] = []
        for pkg in packages:
            if pkg in self._installed_pip_packages:
                continue
            name = pkg['name']
            version = pkg.get('version', '')
            if version:
                if version[0] not in [">", "<", "="]:
                    version = "==" + version
            _packages.append(f"{name}{version}")
            _repos.append(name)

        if not _packages:
            return

        cmd = ["python3", "-m", "pip", "install", *_packages]
        if source_url:
            cmd = [*cmd, "--extra-index-url", source_url]
        self.run_proc(cmd)

        self._installed_pip_packages.extend(_repos)
        self._installed_pip_packages = list(set(self._installed_pip_packages))

    def install_git_packages(self, settings_reader: SettingsReader) -> List[SettingsReader]:
        sub_settings_readers: List[SettingsReader] = []
        for git_chanel in settings_reader.get_git_channels():
            source_url = git_chanel.get("source").strip("/")
            packages = git_chanel.get("packages")
            for package in packages:
                sub_settings = self._install_git_package(package, source_url, settings_reader)

                if sub_settings:
                    sub_settings_readers.append(sub_settings)

        return sub_settings_readers

    def _install_git_package(
            self, package: GitPackage, source_url: str, settings_reader: SettingsReader) -> Optional[SettingsReader]:
        repo_name = package["name"]

        # skip install if the package is already installed
        if repo_name in self._installed_git_packages:
            return None

        is_brick = package.get("is_brick", False)
        version = package.get("version", "")

        repo_path = f"{source_url}/{repo_name}.git"
        print(f"Cloning git repository {repo_path}:{version} ... ")
        repo_path = self.format_url(repo_path, settings_reader.get_environment_variables())

        if is_brick:
            sub_settings = self.install_brick_git_package(repo_name, version, repo_path, settings_reader.get_name())
        else:
            sub_settings = self.install_other_git_package(repo_name, version, repo_path)

        self._installed_git_packages.append(repo_name)
        return sub_settings

    def install_brick_git_package(self, brick_name: str, version: str, repo_path: str,
                                  parent_name: str) -> SettingsReader:
        # Set hidden to False only if the brick is in the user bricks dir
        # normally this is only in dev env
        is_hidden = not os.path.exists(os.path.join(self.USER_BRICKS_FOLDER, brick_name)) or self.env_mode == 'GLAB'

        # retrieve brick repo
        repo_dir: str = None
        if is_hidden:
            repo_dir = os.path.join(self.SYS_BRICKS_FOLDER, brick_name)
        else:
            repo_dir = os.path.join(self.USER_BRICKS_FOLDER, brick_name)

        cloned_package: ClonedPackage = None
        if os.path.exists(repo_dir):
            # update hidden bricks (remove and clone)
            if is_hidden:
                print(f"Removing {repo_dir} ...")
                try:
                    shutil.rmtree(repo_dir)
                except:
                    raise Exception(f"Cannot remove {repo_dir}")
                cloned_package = self.git_clone(repo_path, repo_dir, brick_name, version=version)
            else:
                print(f"Do not update non-hidden brick {repo_dir}")
        else:
            cloned_package = self.git_clone(repo_path, repo_dir, brick_name, version=version)

        if cloned_package:
            self.create_brick_installation_file(
                name=brick_name, path=repo_dir, parent_name=parent_name, git_hash=cloned_package["git_hash"],
                version=cloned_package["version"],
                package_type='git')

        if not os.path.exists(repo_dir):
            raise Exception(f"Brick package {brick_name} version {version} could not be installed.")

        # return the sub settings so the sub dependencies can be installed
        return SettingsReader(os.path.join(repo_dir, self.SETTING_JSON_FILE))

    def install_other_git_package(self, repo_name: str, version: str, repo_path: str) -> None:

        repo_dir = os.path.join(self.EXTERNAL_LIB_FOLDER, repo_name)

        if os.path.exists(repo_dir):
            print(f"Removing {repo_dir} ...")
            try:
                shutil.rmtree(repo_dir)
            except:
                raise Exception(f"Cannot remove {repo_dir}")
        self.git_clone(repo_path, repo_dir, repo_name)

        if not os.path.exists(repo_dir):
            raise Exception(f"Git package {repo_name} version {version} could not be installed.")

    def git_clone(self, url: str, dest_dir: str, repo_name: str, version: str = None) -> ClonedPackage:
        # Try to clone the repository 3 times if it fails
        repo: Repo
        nb_retry = 0
        while True:
            try:
                if version:
                    repo = Repo.clone_from(url=url, to_path=dest_dir, branch=version, depth=1)
                else:
                    repo = Repo.clone_from(url=url, to_path=dest_dir, depth=1)
                break
            except Exception as err:
                print(f"Couldn't clone the repository '{repo_name}' with version '{version}'. Error: {err}")
                print("Waiting 3 secs and retry ...")
                time.sleep(3)
                nb_retry += 1
                if nb_retry >= 3:
                    raise err

        # store info about the git
        clone_package: ClonedPackage = {
            "version": version,
            "git_hash": repo.head.object.hexsha,
            "name": repo_name,
            "path": dest_dir
        }

        # remove .git folder
        try:
            print(f"Removing .git directory from {dest_dir} ...")
            shutil.rmtree(os.path.join(dest_dir, ".git"))
        except:
            raise Exception(f"Cannot remove .git directory from {dest_dir}")

        return clone_package

    def install_app_entrypoint(self):
        """Create the fake app brick for the entrypoint with the manage.py start file
        and the settings.json file
        """

        # get manage.py file path, it the same folder as current file
        manage_py_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manage.py")
        manage_file_destination = os.path.join(self.APP_BRICK_FOLDER, "manage.py")
        print(f"Copying manage.py file from {manage_py_file} to {manage_file_destination} ... ")
        shutil.copyfile(manage_py_file, manage_file_destination)

        # Really important, update the settings.json file with main config info so the bricks will be loaded on start
        settings_file = os.path.join(self.APP_BRICK_FOLDER, self.SETTING_JSON_FILE)

        settings = {
            "name": self.config_reader.get_name(),
            "version": "1.0.0",
            "variables": self.config_reader.get_variables(),
            "environment": self.config_reader.get_environment()
        }
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4)

    def install_notebook_entrypoint(self):

        tempalate_dir = os.path.join(self.NOTEBOOK_FOLDER, "template")
        if os.path.exists(tempalate_dir):
            return

        __cdir__ = os.path.dirname(os.path.abspath(__file__))
        shutil.copytree(
            os.path.abspath(os.path.join(__cdir__, '..', "notebook_template")),
            tempalate_dir
        )

    def format_url(self, string: str, variables: Dict[str, str]) -> str:
        if not string:
            return string

        if not variables:
            variables = {}

        global_config_vars = self.config_reader.get_environment_variables()

        tab = re.findall(r"\$\{?([A-Z_]*)\}?", string)  # re.findall(r"\${?[A-Z_]}?*", string)
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
                        raise Exception(f"No environment variable {token} found")

            if value:
                string = re.sub(r"\$\{?"+token+r"\}?", value, string)

        return string

    def list_all_brick_paths(self) -> List[str]:

        user_bricks = self.get_bricks_in_folder(self.USER_BRICKS_FOLDER)
        sys_bricks = self.get_bricks_in_folder(self.SYS_BRICKS_FOLDER)

        user_bricks.extend(sys_bricks)
        return user_bricks

    def get_bricks_in_folder(self, path: str) -> List[str]:
        """return a list of all the bricks in the provided folder
        """
        brick_paths = []
        for brick_folder in os.listdir(path):
            brick_path = os.path.join(path, brick_folder)
            if self.folder_is_brick(brick_path):
                brick_paths.append(brick_path)
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

    @staticmethod
    def run_proc(cmd, cwd=None) -> bool:
        if cwd:
            if not os.path.exists(cwd):
                os.makedirs(cwd)
        try:
            subprocess.check_call(cmd, stdout=subprocess.DEVNULL, cwd=cwd)
            return True
        except:
            return False

    def configure_vscode(self) -> None:
        if self.env_mode != 'CODELAB':
            return

        print("Configuring VS Code ...")

        vs_code_folder = self.get_vs_code_setting_folder()
        setting_path = self.get_vs_code_setting_file_path()
        default_path = self.VS_CODE_DEFAULT_CONFIG_PATH

        if not os.path.exists(vs_code_folder):
            os.mkdir(vs_code_folder)

        if not os.path.exists(setting_path):
            # copy the settings.json file only if it does not exist
            shutil.copyfile(os.path.join(default_path, 'settings.json'), setting_path)

        # always override the extensions.json file
        shutil.copyfile(os.path.join(default_path, 'extensions.json'), os.path.join(vs_code_folder, 'extensions.json'))
        # always override the launch.json file
        shutil.copyfile(os.path.join(default_path, 'launch.json'), os.path.join(vs_code_folder, 'launch.json'))

        # copy the pylint files
        shutil.copyfile(os.path.join(default_path, '.pylintrc'), os.path.join(self.USER_WORKSPACE_DIR, '.pylintrc'))
        shutil.copyfile(os.path.join(default_path, 'pylint_init.py'),
                        os.path.join(self.USER_WORKSPACE_DIR, 'pylint_init.py'))

        # load the settings file into a dict
        try:
            with open(setting_path, 'r') as f:
                settings = json.load(f)

                # init the extra paths if not already done
                if 'python.autoComplete.extraPaths' not in settings \
                        or not isinstance(settings['python.autoComplete.extraPaths'], list):
                    settings['python.autoComplete.extraPaths'] = []

                # add the brick paths to the extra paths
                extra_paths: List[str] = settings['python.autoComplete.extraPaths']

                for brick_path in self.list_all_brick_paths():
                    brick_full_path = os.path.join(brick_path, self.SOURCE_FOLDER)
                    if brick_full_path not in extra_paths:
                        # add the source folder of the brick to the extra paths
                        extra_paths.append(brick_full_path)

                settings['python.autoComplete.extraPaths'] = extra_paths

            # write the settings file
            with open(setting_path, 'w') as f:
                json.dump(settings, f, indent=2)

        except Exception as err:
            print(f"Error during parsing or writting the settings file : {err}")
            return

    def get_vs_code_setting_folder(self) -> str:
        return os.path.join(self.USER_WORKSPACE_DIR, ".vscode")

    def get_vs_code_setting_file_path(self) -> str:
        return os.path.join(self.get_vs_code_setting_folder(), "settings.json")

    def create_brick_installation_file(self, name: str, path: str, parent_name: str, version: str,
                                       git_hash: str, package_type:  Literal["pip", "git"]) -> None:
        """Create a file in the brick directory containing the brick installation info for logging purpose
        """

        brick_installation: BrickInstalationInfo = {
            "name": name,
            "version": version,
            "parent_name": parent_name,
            "git_hash": git_hash,
            "package_type": package_type,
            "path": path,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        brick_installation_file = os.path.join(path, self.BRICK_INSTALLATION_FILE)
        with open(brick_installation_file, 'w') as f:
            json.dump(brick_installation, f, indent=2)
