
# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

# Gencovery Package Manager

import click
import git
import os, sys, json
import requests
from zipfile import ZipFile
import json
import subprocess
import shutil
#import virtualenv
import pip

GIT_URL = "https://bitbucket.org/gencovery"

__cdir__ = os.path.dirname(os.path.abspath(__file__))
IS_TEST = False
ROOT_DIR = ""

BRICK_DIR = ""
DATA_DIR = ""
LAB_DIR = ""
LOG_DIR = ""
EXTERN_DIR = ""
TMP_DIR = ""

PACKAGES = []

@click.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True
))
@click.pass_context
@click.option('--pull', help='Pull a brick')
@click.option('--push', help="Push a brick")
@click.option('--build', is_flag=True, help="Build docker image")
@click.option('--start', is_flag=True, help="Start docker container")
@click.option('--stop', is_flag=True, help="Stop docker container")
@click.option('--test', is_flag=True, help="Test mode")
@click.option('--userorigin', default="", help="The url of the userorigin server")
def main(ctx, pull, push, build, start, stop, test, userorigin):
    global ROOT_DIR
    global IS_TEST
    IS_TEST = test
    
    # gws workspace
    _set_cwd(workspace="./gws/")
    _create_dirs()

    if pull:
        git_pull(repo_name=pull)
    elif push:
        git_push(repo_name=pull)
        pass

    # user workspace
    _set_cwd(workspace="./user/")
    _create_dirs()
    user_git_origin_exists = (userorigin != "")
    if user_git_origin_exists:
        if pull:
            git_pull(repo_name=pull, userorigin=userorigin, username="", userpwd="")
        else:
            pass
    
    # allways create a default lab
    lab_dirs = [f.path for f in os.scandir(LAB_DIR) if f.is_dir()]
    if len(lab_dirs) == 0:
        _istall_skeleton_to_lab()

# -- B --

def _build_repo_url(repo_name, userorigin=GIT_URL):
    return userorigin + "/" + repo_name.strip("/") + ".git"

def _build_repo_dir_path(repo_name, repo_type):
    if repo_type == "brick":
        return os.path.join(BRICK_DIR, repo_name)
    elif repo_type == "lab":
        return os.path.join(LAB_DIR, repo_name)
    else:
        return os.path.join(EXTERN_DIR, repo_name)

def _build_tmp_repo_dir_path(repo_name):
    return os.path.join(TMP_DIR, repo_name)

def _is_installed(repo_name):
    return  _is_installed_brick(repo_name) or \
            _is_installed_lab(repo_name) or \
            _is_installed_extern(repo_name)

# -- C --

if __name__ == "__main__":
    main()
    