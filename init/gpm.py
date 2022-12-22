# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import copy
import json
import os
import re
import shutil
import subprocess
import time
from typing import List, Optional, TypedDict, Literal
from .config_reader import SettingsReader 
import click

# ####################################################################
#
# GPM class
#
# ####################################################################
EnvMode = Literal['GLAB', 'CODELAB']

UPDATE_GIT_BRICKS = os.getenv("UPDATE_GIT_BRICKS", None) in ["1", 1]
SKELETON_GIT_ENVIRONMENT = {
    "source": "https://$GWS_GIT_LOGIN:$GWS_GIT_PWD@gitlab.com/gencovery/core",
    "packages": [
        {"name": "skeleton", "version": "", "is_brick": True, "is_hidden": False}
    ]
}

class GitPackage(TypedDict):
    name: str
    version: str
    is_brick: bool


class GPM():
    """
    Package manager
    """
    LAB_WORKSPACE_DIR: str = "/lab/"
    CONFIG_FILE_PATH: str = "/conf/config.json"
    SYS_WORKSPACE_DIR: str = None
    USER_WORKSPACE_DIR: str = None
    GLOBAL_CONFIG: dict = None
    SETTING_JSON_FILE: str = "settings.json"

    SOURCE_FOLDER: str = 'src'
    # path where the default config for vs code is stored (it need to be copied to the user workspace)
    VS_CODE_DEFAULT_CONFIG_PATH = "/.vs-code-server-config"

    config_reader: SettingsReader = None
    _installed_pip_packages: list = []
    _installed_git_packages: list = []

    env_mode: EnvMode = None

    def __init__(self, settings_file_path: str, env_mode: EnvMode):
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
        if not GPM.GLOBAL_CONFIG:
            GPM.GLOBAL_CONFIG = copy.deepcopy(self.config_reader.settings)

        GPM.SYS_WORKSPACE_DIR = os.path.join(GPM.LAB_WORKSPACE_DIR, ".sys")
        GPM.USER_WORKSPACE_DIR = os.path.join(GPM.LAB_WORKSPACE_DIR, "user")

    def init_all(self):
        self.install_pip_and_git_packages()
        self.install_app_entrypoint()
        self.install_notebook_entrypoint()
        self.configure_vscode()


    def format_url(self, string: str) -> str:
        if not string:
            return string
        local_config_vars = self.config_reader.get_environment_variables()
        global_config_vars = GPM.GLOBAL_CONFIG.get("environment", {}).get("variables", {})

        tab = re.findall(r"\$\{?([A-Z_]*)\}?", string)  # re.findall(r"\${?[A-Z_]}?*", string)
        for token in tab:
            # search for values in local variable first
            value = local_config_vars.get(token)
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

    # -- G --

    def git_clone(self, url: str, dest_dir: str, version: str=None) -> None:
        print(f"Cloning git repository {url}:{version} ... ")
        url = self.format_url(url)
        # cmd = ["git", "clone", "--depth", "1", "--no-single-branch", url, dest_dir]
        if version:
            cmd = ["git", "clone", "-b", version, "--depth", "1", url, dest_dir]
        else:
            cmd = ["git", "clone", "--depth", "1", url, dest_dir]

        OK = GPM.run_proc(cmd, cwd=dest_dir)
        nb_retry = 0
        while not OK:
            print("Waiting 3 secs and retry ...")
            time.sleep(3)
            OK = GPM.run_proc(cmd, cwd=dest_dir)
            nb_retry += 1
            if nb_retry >= 3:
                print(f"Couldn't clonde the repository '{url}' with version '{version}'")
                return False

        # remove .git folder
        try:
            print(f"Removing .git directory from {dest_dir} ...")
            shutil.rmtree(os.path.join(dest_dir, ".git"))
        except:
            raise Exception(f"Cannot remove .git directory from {dest_dir}")

        # self._remove_git_credentials_from_config(dest_dir)

    # def _remove_git_credentials_from_config(self, dest_dir):
    #     file = os.path.join(dest_dir, "./.git/config")
    #     with open(file, "r", encoding="utf-8") as fp:
    #         text = fp.read()
    #         cleaned_text = re.sub(r"(https?://)(.*@)?(.+)", r"\1\3", text)
    #     if cleaned_text != text:
    #         with open(file, "w", encoding="utf-8") as fp:
    #             fp.write(cleaned_text)

    # -- I --

    def install_pip_and_git_packages(self):
        # install pip packages
        print("Installing Pip packages ...")
        for pip_channel in self.config_reader.get_pip_channels():
            source_url = pip_channel.get("source")
            packages = pip_channel.get("packages")
            self._install_pip_packages(packages, source_url=source_url)

        # install git packages
        print("Installing Git packages ...")
        self.install_git_packages([self.config_reader])


    def _install_pip_packages(self, packages: list, source_url=None):
        _packages: List[str] = []
        _repos: List[str] = []
        for pkg in packages:
            if pkg in GPM._installed_pip_packages:
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

        source_url = self.format_url(source_url)
        cmd = ["python3", "-m", "pip", "install", *_packages]
        if source_url:
            cmd = [*cmd, "--extra-index-url", source_url]
        GPM.run_proc(cmd)

        GPM._installed_pip_packages.extend(_repos)
        GPM._installed_pip_packages = list(set(GPM._installed_pip_packages))

    def install_git_packages(self, settings_readers: List[SettingsReader]):
        """Recursive method to install git packages. The sub packages are installed after the main packages.

        :param settings_readers: _description_
        :type settings_readers: List[SettingsReader]
        """
       
        sub_settings_readers: List[SettingsReader] = []
        for settings_reader in settings_readers:
          for git_chanel in settings_reader.get_git_channels():
              source_url = git_chanel.get("source").strip("/")
              packages = git_chanel.get("packages")
              for package in packages:
                  sub_settings = self._install_git_package(package, source_url)

                  if sub_settings:
                    sub_settings_readers.append(sub_settings)

        # recusrive call to install sub packages
        # the sub packages are install after the main packages
        if sub_settings_readers:
          self.install_git_packages(sub_settings_readers)
        


    def _install_git_package(self, package: GitPackage, source_url: str) -> Optional[SettingsReader]:
        repo_name = package["name"]

        # skip install if the package is already installed
        if repo_name in self._installed_git_packages:
            return None


        is_brick = package.get("is_brick", False)
        version = package.get("version", "")

        repo_path = f"{source_url}/{repo_name}.git"

        if is_brick:
          sub_settings = self.install_brick_git_package(repo_name, version, repo_path)
        else:
          sub_settings = self.install_other_git_package(repo_name, version, repo_path)

        self._installed_git_packages.append(repo_name)
        return sub_settings


    def install_brick_git_package(self, brick_name: str, version: str, repo_path: str) -> SettingsReader:
        user_bricks_dir = self.get_user_brick_dir()
        user_hidden_bricks_dir = self.get_hidden_brick_dir()
      

        # Set hidden to False only if the brick is in the user bricks dir
        # normally this is only in dev env
        is_hidden = not os.path.exists(os.path.join(user_bricks_dir, brick_name)) or self.env_mode == 'GLAB'

        # retrieve brick repo
        repo_dir: str = None
        if is_hidden:
            repo_dir = os.path.join(user_hidden_bricks_dir, brick_name)
        else:
            repo_dir = os.path.join(user_bricks_dir, brick_name)

        if os.path.exists(repo_dir):
            # update hidden bricks (remove and clone)
            if is_hidden:
                print(f"Removing {repo_dir} ...")
                try:
                    shutil.rmtree(repo_dir)
                except:
                    raise Exception(f"Cannot remove {repo_dir}")
                self.git_clone(repo_path, repo_dir, version=version)
            else:
                print(f"Do not update non-hidden brick {repo_dir}")
        else:
            self.git_clone(repo_path, repo_dir, version=version)
      

        if not os.path.exists(repo_dir):
            raise Exception(f"Brick package {brick_name} version {version} could not be installed.")

        # return the sub settings so the sub dependencies can be installed
        return SettingsReader(os.path.join(repo_dir, self.SETTING_JSON_FILE))

    def install_other_git_package(self, repo_name: str, version: str, repo_path: str) -> None:
        extern_lib_dir = self.get_external_lib_dir() 
        
        repo_dir = os.path.join(extern_lib_dir, repo_name)
        
        if os.path.exists(repo_dir):
            print(f"Removing {repo_dir} ...")
            try:
                shutil.rmtree(repo_dir)
            except:
                raise Exception(f"Cannot remove {repo_dir}")
        self.git_clone(repo_path, repo_dir)

        if not os.path.exists(repo_dir):
            raise Exception(f"Git package {repo_name} version {version} could not be installed.")


    def install_app_entrypoint(self):
        dest_dir = os.path.join(self.SYS_WORKSPACE_DIR, "app")
        skeleton_dir = os.path.join(self.USER_WORKSPACE_DIR, "bricks", "skeleton")
        if not os.path.exists(skeleton_dir):
            skeleton_dir = os.path.join(self.get_hidden_brick_dir(), "skeleton")
            if not os.path.exists(skeleton_dir):
                raise Exception("The skeleton is not found")

        if os.path.exists(dest_dir):
            try:
                print(f"Removing {dest_dir} ...")
                shutil.rmtree(dest_dir, ignore_errors=True)
            except:
                raise Exception(f"Cannot remove {dest_dir}")

        shutil.copytree(
            skeleton_dir,
            dest_dir
        )
        # rename module
        shutil.move(
            os.path.join(dest_dir, self.SOURCE_FOLDER, "skeleton"),
            os.path.join(dest_dir, self.SOURCE_FOLDER, self.config_reader.get_name())
        )

        # remove .git folder
        if os.path.exists(os.path.join(dest_dir, ".git")):
            try:
                print(f"Removing .git directory from {dest_dir} ...")
                shutil.rmtree(os.path.join(dest_dir, ".git"))
            except:
                raise Exception(f"Cannot remove .git directory in {dest_dir}")

        # update settings.json
        settings_file = os.path.join(dest_dir, self.SETTING_JSON_FILE)
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            settings["name"] = self.config_reader.get_name()
            settings["variables"] = self.config_reader.get_variables()
            settings["environment"] = self.config_reader.get_environment()
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4)
        # replace all words 'skeleton' in app.py
        file_path = os.path.join(dest_dir, self.SOURCE_FOLDER, self.config_reader.get_name(), "./app.py")
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            text = text.replace("skeleton", self.config_reader.get_name())
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        # replace all words 'skeleton' in README.md
        file_path = os.path.join(dest_dir, "./README.md")
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            text = text.replace("skeleton", self.config_reader.get_name())
            text = text.replace("Skeleton", self.config_reader.get_name().title())
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)

    def install_notebook_entrypoint(self):
        notebook_dir = os.path.join(self.LAB_WORKSPACE_DIR, "user", "notebooks")
        if not os.path.exists(notebook_dir):
            os.makedirs(notebook_dir)

        tempalate_dir = os.path.join(notebook_dir, "template")
        if os.path.exists(tempalate_dir):
            return

        __cdir__ = os.path.dirname(os.path.abspath(__file__))
        shutil.copytree(
            os.path.join(__cdir__, "notebook_template"),
            tempalate_dir
        )

    def get_user_brick_dir(self) -> str:
        dir = os.path.join(self.USER_WORKSPACE_DIR, "bricks")
        if not os.path.exists(dir):
            os.makedirs(dir)
        return dir

    def get_hidden_brick_dir(self) -> str:
        dir = os.path.join(self.USER_WORKSPACE_DIR, "bricks", ".lib")
        if not os.path.exists(dir):
            os.makedirs(dir)
        return dir

    def get_external_lib_dir(self) -> str:
        dir = os.path.join(self.SYS_WORKSPACE_DIR, "lib")
        if not os.path.exists(dir):
            os.makedirs(dir)
        return dir

    def list_all_brick_paths(self) -> List[str]:

        user_bricks = self.get_bricks_in_folder(self.get_user_brick_dir())
        hidden_bricks = self.get_bricks_in_folder(self.get_hidden_brick_dir())

        user_bricks.extend(hidden_bricks)
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

    def read_config(self) -> dict:
        with open(self.settings_file_path, 'r', encoding="utf-8") as f:
            try:
                config = json.load(f)
                if not config.get("environment"):
                    config["environment"] = {}
                if not config["environment"].get("git"):
                    config["environment"]["git"] = []

                for g in config["environment"]["git"]:
                    if g["source"] == SKELETON_GIT_ENVIRONMENT["source"]:
                        for pkg in g["packages"]:
                            sklt_pkg = SKELETON_GIT_ENVIRONMENT["packages"][0]
                            if pkg["name"] == sklt_pkg["name"]:
                                return config

                # skeleton brick does not exists
                config["environment"]["git"].append(SKELETON_GIT_ENVIRONMENT)
                return config

            except Exception as err:
                raise Exception("Cannot parse the config file. Please check file config file.") from err

    def configure_vscode(self) -> None:
        if self.env_mode != 'CODELAB':
          return

        vs_code_folder = self.get_vs_code_setting_folder()
        setting_path = self.get_vs_code_setting_file_path()
        if not os.path.exists(vs_code_folder):
            os.mkdir(vs_code_folder)
            default_path = self.VS_CODE_DEFAULT_CONFIG_PATH
            # copy the settings.json file only if it does not exist
            shutil.copyfile(os.path.join(default_path, 'settings.json'), setting_path)
            
        # always override the extensions.json file
        shutil.copyfile(os.path.join(default_path, 'extensions.json'), os.path.join(vs_code_folder, 'extensions.json'))
        # always override the launch.json file
        shutil.copyfile(os.path.join(default_path, 'launch.json'), os.path.join(vs_code_folder, 'launch.json'))


        # copy the pylint files
        shutil.copyfile(os.path.join(default_path, '.pylintrc'), os.path.join(self.USER_WORKSPACE_DIR, '.pylintrc'))
        shutil.copyfile(os.path.join(default_path, 'pylint_init.py'), os.path.join(self.USER_WORKSPACE_DIR, 'pylint_init.py'))

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
                  if brick_path not in extra_paths:
                      # add the source folder of the brick to the extra paths
                      extra_paths.append(os.path.join(brick_path, self.SOURCE_FOLDER))

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

    


@click.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True
))
@click.pass_context
@click.option('--env-mode')
def install(ctx, env_mode: EnvMode = None):
    print(f"Initializing GPM with env mode: {env_mode}")

    gpm = GPM(settings_file_path=GPM.CONFIG_FILE_PATH, env_mode=env_mode)
    gpm.init_all()

    print(f"Installed pip packages:\n{GPM._installed_pip_packages}")
    print(f"Installed git packages:\n{GPM._installed_git_packages}")


if __name__ == "__main__":
    install()
