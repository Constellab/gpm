# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import os
import shutil
import git
import subprocess
import re
import json
import urllib
import glob
import time
import gpm_credentials # @ToDo: remove gpm_credentials later
import click

# ####################################################################
#
# GPM class
#
# ####################################################################

class GPM():
    """
    Package manager
    """
    LAB_WORKSPACE_DIR = "/lab/"
    CONFIG_FILE_PATH = "/conf/config.json"

    def __init__(self, settings_file_path):
        self.settings_file_path = settings_file_path
        self.config = self.read_config()
        self.SYS_WORKSPACE_DIR = os.path.join(self.LAB_WORKSPACE_DIR, ".sys")
        self.USER_WORKSPACE_DIR = os.path.join(self.LAB_WORKSPACE_DIR, "user")

    # -- F --

    def format_url( self, string: str ) -> str:
        if not string:
            return string
        variables = self.config.get("environment",{}).get("variables",{})
        tab = re.findall(r"\$[A-Za-z_]*", string)
        for token in tab:
            token = token[1:]
            # search for values in local variable first
            value = variables.get(token)
            if not value:
                # search for values in global environment
                value = os.getenv(token)
                # special case (git crendetials encrypted here!)
                if not value:
                    if token == "GWS_GIT_LOGIN":
                        value = gpm_credentials.CREDENTIALS.get_git_credentials()[0]
                    if token == "GWS_GIT_PWD":
                        value = gpm_credentials.CREDENTIALS.get_git_credentials()[1]

            if value:
                string = string.replace("$"+token, value)        
        return string

    # -- G --

    def git_clone(self, url, dest_dir, branch=None, commit_sha=None):
        print(f"Cloning git repository {url} ... ")
        url = self.format_url(url)
        cmd = ["git", "clone", "--depth", "1", "--no-single-branch", url, dest_dir]
        OK = GPM.run_proc(cmd, cwd=dest_dir)
        nb_retry = 0
        while not OK:
            print(f"Waiting 3 secs and retry ...")
            time.sleep(3)
            OK = GPM.run_proc(cmd, cwd=dest_dir)
            nb_retry += 1
            if nb_retry >= 3:
                print(f"Failed!")
                return False
        
        if branch:
            cmd = ["git", "checkout", branch]
            if commit_sha:
                cmd = [*cmd, commit_sha]
            return GPM.run_proc(cmd, cwd=dest_dir)
        else:
            return True

    def git_pull(self, dest_dir, branch=None, commit_sha=None):
        print(f"Pulling git repository {dest_dir} ... ")
        if branch:
            cmd = ["git", "checkout", branch]
            if commit_sha:
                cmd = [*cmd, commit_sha]
            GPM.run_proc(cmd, cwd=dest_dir)
        cmd = ["git", "pull"]
        OK = GPM.run_proc(cmd, cwd=dest_dir)
        print("Done!")
        return OK

    # -- I --

    def install_pip_and_git_packages(self):
        env = self.config.get("environment")
        # install pip packages
        print(f"Installing Pip packages ...")
        for channel in env.get("pip",[]):
            source_url = channel.get("source")
            packages = channel.get("packages")
            self._install_pip_packages(packages, source_url=source_url)
        # install git packages
        print(f"Installing Git packages ...")
        for channel in env.get("git",[]):
            source_url = channel.get("source").strip("/")
            packages = channel.get("packages")
            for package in channel.get("packages"):
                self._install_git_packages(package, source_url)

    def install_app_entrypoint(self):
        dest_dir = os.path.join(self.SYS_WORKSPACE_DIR, "app")
        skeleton_dir = os.path.join(self.USER_WORKSPACE_DIR, "bricks", "skeleton")
        if not os.path.exists(skeleton_dir):
            raise Exception("The skeleton is not found")
        if os.path.exists(dest_dir):
            shutil.rmtree(dest_dir, ignore_errors=True)
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
        shutil.rmtree(os.path.join(dest_dir, ".git"))
        # update settings.json
        settings_file = os.path.join(dest_dir, "settings.json")
        with open(settings_file, 'r') as f:
            settings                    = json.load(f)
            settings["name"]            = self.config["name"]
            settings["virtual_host"]    = self.config["virtual_host"]
            settings["variables"]       = self.config["variables"]
            settings["environment"]     = self.config["environment"]
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=4)
        # replace all words 'skeleton' in app.py
        file_path = os.path.join(dest_dir, "src", self.config["name"], "./app.py")
        with open(file_path, 'r') as f:
            text = f.read()
            text = text.replace("skeleton", self.config["name"])
        with open(file_path, 'w') as f:
            f.write(text)
        # replace all words 'skeleton' in README.md
        file_path = os.path.join(dest_dir, "./README.md")
        with open(file_path, 'r') as f:
            text = f.read()
            text = text.replace("skeleton", self.config["name"])
            text = text.replace("Skeleton", self.config["name"].title())
        with open(file_path, 'w') as f:
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
        if not packages:
            return
        source_url = self.format_url(source_url)
        cmd = ["python3", "-m", "pip", "install", *packages]
        if source_url:
            cmd = [*cmd, "--extra-index-url", source_url]
        GPM.run_proc(cmd)
        
    def _install_git_packages(self, package, source_url):
        bricks_dir = os.path.join(self.USER_WORKSPACE_DIR, "bricks")
        externs_dir = os.path.join(self.SYS_WORKSPACE_DIR, "lib")
        repo, commit_sha, branch = self.parse_git_package(package)
        repo_dir = os.path.join(bricks_dir, repo)
        was_in_brick_dir = os.path.exists(repo_dir)
        if was_in_brick_dir:
            self.git_pull(repo_dir, branch=branch, commit_sha=commit_sha) 
        else:
            extern_repo_dir = os.path.join(externs_dir, repo)
            was_in_externs_dir = os.path.exists(extern_repo_dir)
            if was_in_externs_dir:
                self.git_pull(extern_repo_dir, branch=branch, commit_sha=commit_sha)
                return
            else:
                source_url = f"{source_url}/{repo}.git"
                self.git_clone(source_url, repo_dir, branch=branch, commit_sha=commit_sha)
        if not os.path.exists(repo_dir):
            print(f"Git package {package} could not be installed.")
            return
        settings_file = os.path.join(repo_dir, "settings.json")
        is_brick = os.path.exists(settings_file)
        if is_brick:
            print(f"Following dependendies of {package} ...")
            gpm = GPM(settings_file_path=os.path.join(bricks_dir, repo, "settings.json"))
            gpm.install_pip_and_git_packages()
        else:
            print(f"Moving external library {package} to externs dir ... ", end="")
            if not os.path.exists(externs_dir):
                os.makedirs(externs_dir)
            shutil.move(repo_dir, externs_dir)
            print("Done!")

    # -- P --

    def parse_git_package(self, string: str) -> str:
        tab = re.findall(r"\[.+\]$", string)
        if tab:
            string = string.replace(tab[0], "")
            commit_sha = re.match(r".*(c|commit)\s*=\s*([A-Za-z0-9]+).*", tab[0])[2]
            branch = re.match(r".*(b|branch)\s*=\s*([A-Za-z0-9]+).*", tab[0])[2]
            if commit_sha == "latest":
                commit_sha = None
            return string, commit_sha, branch
        return string, None, None

    # -- R --

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
        with open(self.settings_file_path, 'r') as f:
            try:
                return json.load(f)
            except Exception as err:
                raise Exception("Cannot parse the config file. Please check file config file.") from err
        raise Exception("Cannot open the config file")
    
@click.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True
))
@click.pass_context
@click.option('--test', is_flag=True, help='Run tests')
@click.option('--rm', is_flag=True, help='Remove files after testing')
def install(ctx, test=False, rm=False):
    if test:
        __cdir__ = os.path.dirname(os.path.abspath(__file__))
        GPM.LAB_WORKSPACE_DIR = os.path.join(__cdir__, "./tests/build/lab")
        GPM.CONFIG_FILE_PATH = os.path.join(__cdir__, "./tests/config.json")
        gpm = GPM(settings_file_path=GPM.CONFIG_FILE_PATH)
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

if __name__ == "__main__":
    install()
