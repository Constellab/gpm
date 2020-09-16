
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
APP_DIR = os.path.join(__cdir__, "./test")
BRICKS_DIR = os.path.join(APP_DIR, "./gws/bricks")
DATA_DIR = os.path.join(APP_DIR, "./gws/data")
LAB_DIR = os.path.join(APP_DIR, "./gws/labs")
EXTERN_DIR = os.path.join(APP_DIR, "./gws/extern")
TMP_DIR = os.path.join(APP_DIR, "./gws/tmp")

ALL_BRICKS = "all"
PACKAGES = []

def git_pull(repo=ALL_BRICKS):

    private_file = os.path.join(__cdir__, "./.private.json")
    if os.path.exists(private_file):
        with open(private_file) as f:
            private = json.load(f)
    else:
        raise Exception("File .private.json not found")

    git_user = private["git_crenditals"]["login"]
    git_pwd = private["git_crenditals"]["password"]
    os.environ['GIT_ASKPASS'] = os.path.join(__cdir__,'askpass.sh')
    os.environ['GIT_USERNAME'] = git_user
    os.environ['GIT_PASSWORD'] = git_pwd

    PACKAGES = _read_pkgs()

    if repo == ALL_BRICKS:
        for repo in PACKAGES:
            _git_pull_repo(repo, git_user, git_pwd)
    else:
        _git_pull_repo(repo, git_user, git_pwd)

def _git_pull_repo(repo, user, pwd):
    url = _get_repo_url(repo)
    tab = url.split("://")
    #url = f"{tab[0]}://{user}:{pwd}@{tab[1]}"
    url = f"{tab[0]}://{user}@{tab[1]}"

    if _repo_exists(repo):
        print("Git update " + f"{tab[0]}://{tab[1]}")
        repo_dir = _get_repo_dir(repo)
        git_repo = git.Repo(repo_dir)
        o = git_repo.remotes.origin
        o.pull()
    else:
        print("Git clone " + f"{tab[0]}://{tab[1]}")
        tmp_repo_dir = _get_tmp_repo_dir(repo)
        git.Repo.clone_from(url, tmp_repo_dir, branch='master', depth=1, shallow_submodules=True)
        if _is_brick(tmp_repo_dir):
            repo_dir = _get_repo_dir(repo)
        else:
            repo_dir = _get_extern_repo_dir(repo)
        
        shutil.move(tmp_repo_dir, repo_dir)
        git_repo = git.Repo(repo_dir)

    try:
        for sub in git_repo.submodules:
            sub_url = sub.config_reader().get_value("url")
            tab = sub_url.split("://")
            sub_url = f"{tab[0]}://{user}:{pwd}@{tab[1]}"
            sub.config_writer().set_value("url", sub_url).release()
            print("Submodule " + f"{tab[0]}://{tab[1]}")

        git_repo.submodule_update(recursive=True)
    except:
        pass

def _git_push_repo(repo, user, pwd):
    pass

def _is_brick(repo_dir):
    settings_file = os.path.join(repo_dir, "settings.json")
    if os.path.exists(settings_file):
        with open(settings_file) as f:
            try:
                settings = json.load(f)
                return not settings["name"] is None
            except:
                return False
    else:
        return False

def _read_pkgs():
    with open(os.path.join(__cdir__,"packages.json")) as f:
            try:
                return json.load(f)
            except:
                raise Exception("Error while parsing the settings JSON file. Please check file setting file.")

def _get_repo_url(repo):
    return GIT_URL + "/" + repo.strip("/") + ".git"

def _get_repo_dir(repo):
    return os.path.join(BRICKS_DIR, repo)

def _get_tmp_repo_dir(repo):
    return os.path.join(TMP_DIR, repo)

def _get_extern_repo_dir(repo):
    return os.path.join(EXTERN_DIR, repo)

def _repo_exists(repo):
    return os.path.exists( _get_repo_dir(repo) )

def _create_dirs():
    if not os.path.exists(BRICKS_DIR):
        os.makedirs(BRICKS_DIR)
    
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    if not os.path.exists(LAB_DIR):
        os.makedirs(LAB_DIR)
    
    if not os.path.exists(EXTERN_DIR):
        os.makedirs(EXTERN_DIR)
    
    if not os.path.exists(TMP_DIR):
        os.makedirs(TMP_DIR)

# def _install_requirements(repo_dir):
#     venv_dir = os.path.join(APP_DIR, "./.venv")

#     if not os.path.exists(venv_dir):
#         virtualenv.create(venv_dir)

#     execfile(os.path.join(venv_dir, "bin", "activate_this.py"))

#     req_file = os.path.join(repo_dir, "requirements.txt")
#     if os.path.exists(req_file):
#         pip.main(["install", "--prefix", venv_dir, "-r", req_file])
    
def download(url, filename):
    data_url = "https://share.gencovery.com"
    url = data_url + url.strip("/")
    print(f"Downloading {url} ...")
    with open(filename, 'wb') as f:
        response = requests.get(url, stream=True)
        total = response.headers.get('content-length')

        if total is None:
            f.write(response.content)
        else:
            downloaded = 0
            total = int(total)
            for data in response.iter_content(chunk_size=max(int(total/1000), 1024*1024)):
                downloaded += len(data)
                f.write(data)
                done = int(50*downloaded/total)
                sys.stdout.write('\r[{}{}]'.format('█' * done, '.' * (50-done)))
                sys.stdout.flush()
    sys.stdout.write('\n')

def unzip(filename):
    print(f"Extracting {filename} ...")
    with ZipFile(filename, 'r') as zipObj:
        path = os.path.dirname(filename)
        zipObj.extractall(path)
    print(f"Extraction finished.")


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
def run(ctx, pull, push, build, start, stop, test):
    _create_dirs()
    if pull:
        git_pull(repo=pull)
    else:
        pass

if __name__ == "__main__":
    run()
    