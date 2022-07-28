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
from typing import List, TypedDict

import click

# ####################################################################
#
# GPM class
#
# ####################################################################

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

    is_test: bool = False
    config: dict = None
    _installed_pip_packages: list = []
    _installed_git_packages: list = []

    def __init__(self, settings_file_path):
        self.settings_file_path = settings_file_path
        self.config = self.read_config()
        if not GPM.GLOBAL_CONFIG:
            GPM.GLOBAL_CONFIG = copy.deepcopy(self.config)

        GPM.SYS_WORKSPACE_DIR = os.path.join(GPM.LAB_WORKSPACE_DIR, ".sys")
        GPM.USER_WORKSPACE_DIR = os.path.join(GPM.LAB_WORKSPACE_DIR, "user")

    # -- F --

    def format_url(self, string: str) -> str:
        if not string:
            return string
        local_config_vars = self.config.get("environment", {}).get("variables", {})
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
        env = self.config.get("environment", {})
        # install pip packages
        print("Installing Pip packages ...")
        for channel in env.get("pip", []):
            source_url = channel.get("source")
            packages = channel.get("packages")
            self._install_pip_packages(packages, source_url=source_url)

        # install git packages
        print("Installing Git packages ...")
        for channel in env.get("git", []):
            source_url = channel.get("source").strip("/")
            packages = channel.get("packages")
            for package in packages:
                self._install_git_packages(package, source_url)

    def install_app_entrypoint(self):
        dest_dir = os.path.join(self.SYS_WORKSPACE_DIR, "app")
        skeleton_dir = os.path.join(self.USER_WORKSPACE_DIR, "bricks", "skeleton")
        if not os.path.exists(skeleton_dir):
            skeleton_dir = os.path.join(self.USER_WORKSPACE_DIR, "bricks", ".lib", "skeleton")
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
            os.path.join(dest_dir, "src", "skeleton"),
            os.path.join(dest_dir, "src", self.config["name"])
        )

        # remove .git folder
        if os.path.exists(os.path.join(dest_dir, ".git")):
            try:
                print(f"Removing .git directory from {dest_dir} ...")
                shutil.rmtree(os.path.join(dest_dir, ".git"))
            except:
                raise Exception(f"Cannot remove .git directory in {dest_dir}")

        # update settings.json
        settings_file = os.path.join(dest_dir, "settings.json")
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            settings["name"] = self.config["name"]
            settings["variables"] = self.config["variables"]
            settings["environment"] = self.config["environment"]
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4)
        # replace all words 'skeleton' in app.py
        file_path = os.path.join(dest_dir, "src", self.config["name"], "./app.py")
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            text = text.replace("skeleton", self.config["name"])
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        # replace all words 'skeleton' in README.md
        file_path = os.path.join(dest_dir, "./README.md")
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            text = text.replace("skeleton", self.config["name"])
            text = text.replace("Skeleton", self.config["name"].title())
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

    def _install_git_packages(self, package: GitPackage, source_url: str):
        repo_name = package["name"]

        # skip install if the package is already installed
        if repo_name in self._installed_git_packages:
            return


        is_brick = package.get("is_brick", False)
        version = package.get("version", "")

        repo_path = f"{source_url}/{repo_name}.git"

        if is_brick:
          self.install_brick_git_package(repo_name, version, repo_path)
        else:
          self.install_other_git_package(repo_name, version, repo_path)


    def install_brick_git_package(self, brick_name: str, version: str, repo_path: str) -> None:
        user_bricks_dir = self.get_user_brick_dir()
        user_hidden_bricks_dir = self.get_hidden_brick_dir()
      

        # Set hidden to False only if the brick is in the user bricks dir
        # normally this is only in dev env
        is_hidden = not os.path.exists(os.path.join(user_bricks_dir, brick_name))

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

        self._installed_git_packages.append(brick_name)

        # install brick sub dependencies
        print(f"Following dependendies of {brick_name} ...")
        gpm = GPM(settings_file_path=os.path.join(repo_dir, "settings.json"))
        gpm.install_pip_and_git_packages()

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

        self._installed_git_packages.append(repo_name)

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

    # -- P --

    # -- R --

    @ staticmethod
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
        raise Exception("Cannot open the config file")


@ click.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True
))
@ click.pass_context
@ click.option('--test', is_flag=True, help='Run tests')
@ click.option('--rm', is_flag=True, help='Remove files after testing')
def install(ctx, test=False, rm=False):
    if test:
        __cdir__ = os.path.dirname(os.path.abspath(__file__))
        GPM.LAB_WORKSPACE_DIR = os.path.join(__cdir__, "./tests/build/lab")
        GPM.CONFIG_FILE_PATH = os.path.join(__cdir__, "./tests/config.json")
        gpm = GPM(settings_file_path=GPM.CONFIG_FILE_PATH)

        # print(gpm.config)
        # return

        gpm.is_test = True
        gpm.install_pip_and_git_packages()
        gpm.install_app_entrypoint()
        gpm.install_notebook_entrypoint()
        if rm:
            shutil.rmtree(GPM.LAB_WORKSPACE_DIR)
    else:
        gpm = GPM(settings_file_path=GPM.CONFIG_FILE_PATH)
        gpm.install_pip_and_git_packages()
        gpm.install_app_entrypoint()
        gpm.install_notebook_entrypoint()

    print(f"Installed pip packages:\n{GPM._installed_pip_packages}")
    print(f"Installed git packages:\n{GPM._installed_git_packages}")


if __name__ == "__main__":
    install()
