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

__cdir__ = os.path.dirname(os.path.abspath(__file__))

# ####################################################################
#
# GPM class
#
# ####################################################################

class GPM():
    """
    Package manager
    """
    USER_WORKSPACE_DIR = "/lab/user/"
    CONFIG_FILE_PATH = "/conf/config.json"

    def __init__(self, settings_file_path):
        self.settings_file_path = settings_file_path
        self.env = self.read_env()

    # -- F --

    def format_url( self, string: str ) -> str:
        if not string:
            return string
        variables = self.env.get("variables",{})
        tab = re.findall(r"\$[A-Za-z_]*", string)
        for token in tab:
            token = token[1:]
            value = os.getenv(token)
            if not value:
                value = variables.get(token)
                # @ToDo: remove gpm_credentials later
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

    def git_pull(self, url, dest_dir, branch=None, commit_sha=None):
        print(f"Pulling git repository {url} ... ", end="")
        url = self.format_url(url)
        if branch:
            cmd = ["git", "checkout", branch]
            if commit_sha:
                cmd = [*cmd, commit_sha]
            GPM.run_proc(cmd, cwd=dest_dir)
        cmd = ["git", "pull", url]
        OK = GPM.run_proc(cmd, cwd=dest_dir)
        print("Done!")
        return OK

    # -- I --

    def install(self):
        # install pip
        for dep in self.env.get("pip",[]):
            source_url = dep.get("source")
            packages = dep.get("packages")
            self.install_through_pip(packages, source_url=source_url)
        # install git
        for dep in self.env.get("git",[]):
            source_url = dep.get("source").strip("/")
            packages = dep.get("packages")
            for package in dep.get("packages"):
                self.install_through_git(package, source_url)

    def install_through_pip(self, packages: list, source_url=None):
        print(f"Installing Pip packages ...")
        if not packages:
            return
        source_url = self.format_url(source_url)
        cmd = ["python3", "-m", "pip", "install", *packages]
        if source_url:
            cmd = [*cmd, "--extra-index-url", source_url]
        GPM.run_proc(cmd)
        
    def install_through_git(self, package, source_url):
        print(f"Installing Git package {package} ...")
        bricks_dir = os.path.join(self.USER_WORKSPACE_DIR, "bricks")
        externs_dir = os.path.join(self.USER_WORKSPACE_DIR, "externs")
        repo, commit_sha, branch = self.parse_git_package(package)
        repo_dir = os.path.join(bricks_dir, repo)
        source_url = f"{source_url}/{repo}.git"

        was_in_brick_dir = os.path.exists(repo_dir)
        if was_in_brick_dir:
            self.git_pull(source_url, repo_dir, branch=branch, commit_sha=commit_sha) 
        else:
            extern_repo_dir = os.path.join(externs_dir, repo)
            was_in_externs_dir = os.path.exists(extern_repo_dir)
            if was_in_externs_dir:
                self.git_pull(source_url, extern_repo_dir, branch=branch, commit_sha=commit_sha)
                return
            else:
                self.git_clone(source_url, repo_dir, branch=branch, commit_sha=commit_sha)

        if not os.path.exists(repo_dir):
            print(f"Git package {package} could not be installed.")
            return

        settings_file = os.path.join(repo_dir, "settings.json")
        is_brick = os.path.exists(settings_file)
        if is_brick:
            print(f"Following dependendies of {package} ...")
            gpm = GPM(settings_file_path=os.path.join(bricks_dir, repo, "settings.json"))
            gpm.install()
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

    def read_env(self) -> dict:
        with open(self.settings_file_path, 'r') as f:
            try:
                return json.load(f).get("environment")
            except Exception as err:
                raise Exception("Cannot parse the config file. Please check file config file.") from err
        raise Exception("Cannot open the config file")
    
@click.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True
))
@click.pass_context
@click.option('--test', is_flag=True, help='Test gmp')
@click.option('--rm', is_flag=True, help='Remove files after testing')
def install(ctx, test=False, rm=False):
    if test:
        GPM.USER_WORKSPACE_DIR = os.path.join(__cdir__, "./tests/build")
        GPM.CONFIG_FILE_PATH = os.path.join(__cdir__, "./tests/config.json")
        gpm = GPM(settings_file_path=GPM.CONFIG_FILE_PATH)
        gpm.install()
        if rm:
            shutil.rmtree(GPM.USER_WORKSPACE_DIR)
    else:
        gpm = GPM(settings_file_path=GPM.CONFIG_FILE_PATH)
        gpm.install()

if __name__ == "__main__":
    install()
