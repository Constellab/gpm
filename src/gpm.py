
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
APP_DIR = ""
BRICKS_DIR = ""
DATA_DIR = ""
LAB_DIR = ""
EXTERN_DIR = ""
TMP_DIR = ""
ALL_BRICKS = "all"
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
@click.option('--origin', '-o', default=GIT_URL, help="The url of the origin server")
def main(ctx, pull, push, build, start, stop, test, origin):
    global APP_DIR
    global IS_TEST
    IS_TEST = test
    
    _set_dir_paths(workspace=f"./user/")
    _create_dirs()

    _set_dir_paths()
    _create_dirs()

    if pull:
        git_pull(repo=pull, origin=origin)
    else:
        pass

def git_pull(repo=ALL_BRICKS, origin=GIT_URL):

    private_file = os.path.join(__cdir__, "../.private.json")
    if os.path.exists(private_file):
        with open(private_file, 'r') as f:
            private = json.load(f)
    else:
        raise Exception("File .private.json not found")

    git_user = private["git"]["login"]
    git_pwd = private["git"]["password"]

    import crypt
    if not git_pwd:
        raise Exception("The private file does not exist")
    elif len(git_pwd) < 64:
        git_pwd = crypt.encrypt_message(git_pwd)
        private["git"]["password"] = git_pwd
        with open(private_file, 'w') as f:
            json.dump(private, f)
    else:
        _git_pwd = crypt.decrypt_message(git_pwd)
        git_pwd = ""
        for i in range(0, len(_git_pwd), 2):
            git_pwd = git_pwd + _git_pwd[i]

    os.environ['GIT_ASKPASS'] = os.path.join(__cdir__,'askpass.sh')
    os.environ['GIT_USERNAME'] = git_user
    os.environ['GIT_PASSWORD'] = git_pwd

    PACKAGES = _read_pkgs()

    if repo == ALL_BRICKS:
        for repo in PACKAGES:
            _git_pull_repo(repo, git_user, git_pwd, origin)
    else:
        _git_pull_repo(repo, git_user, git_pwd, origin)

def _set_dir_paths(workspace="./"):
    global APP_DIR
    global BRICKS_DIR
    global DATA_DIR
    global LAB_DIR
    global EXTERN_DIR
    global TMP_DIR

    if IS_TEST:
        APP_DIR = os.path.join(__cdir__, "../../tests/")
    else:
        APP_DIR = os.path.join(__cdir__, "../../")

    BRICKS_DIR = os.path.join(APP_DIR, workspace, "./gws/bricks")
    DATA_DIR = os.path.join(APP_DIR, workspace, "./gws/data")
    LAB_DIR = os.path.join(APP_DIR, workspace, "./gws/labs")
    EXTERN_DIR = os.path.join(APP_DIR, workspace, "./gws/extern")
    TMP_DIR = os.path.join(APP_DIR, workspace, "./gws/tmp")

def _git_pull_repo(repo, user, pwd, origin=GIT_URL):
    url = _get_repo_url(repo, origin)
    tab = url.split("://")
    url = f"{tab[0]}://{user}:{pwd}@{tab[1]}"
    #url = f"{tab[0]}://{user}@{tab[1]}"

    if _repo_exists(repo):
        print("Git update {repo} from " + f"{tab[0]}://{tab[1]}")
        repo_dir = _get_repo_dir(repo)
        git_repo = git.Repo(repo_dir)
        o = git_repo.remotes.origin
        o.pull()
    else:
        print(f"Git clone brick {repo} from " + f"{tab[0]}://{tab[1]}")
        tmp_repo_dir = _get_tmp_repo_dir(repo)
        if IS_TEST:
            git.Repo.clone_from(url, tmp_repo_dir, branch='master', depth=1, shallow_submodules=True)
        else:
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
            import re
            tab = re.split("://.+@", sub_url)
            sub_url = f"{tab[0]}://{user}:{pwd}@{tab[1]}"
            sub.config_writer().set_value("url", sub_url).release()
            print("Getting submodule " + f"{tab[0]}://{tab[1]}")

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
    with open(os.path.join(__cdir__,"../packages.json")) as f:
            try:
                return json.load(f)
            except:
                raise Exception("Error while parsing the settings JSON file. Please check file setting file.")

def _get_repo_url(repo, origin=GIT_URL):
    return origin + "/" + repo.strip("/") + ".git"

def _get_repo_dir(repo):
    return os.path.join(BRICKS_DIR, repo)

def _get_tmp_repo_dir(repo):
    return os.path.join(TMP_DIR, repo)

def _get_extern_repo_dir(repo):
    return os.path.join(EXTERN_DIR, repo)

def _repo_exists(repo):
    return os.path.exists( _get_repo_dir(repo) )

def _create_dirs(wkspace=""):
    if not os.path.exists(BRICKS_DIR):
        os.makedirs(BRICKS_DIR)
    else:
        raise Exception(f"Path {BRICKS_DIR} already exists")

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    if not os.path.exists(LAB_DIR):
        os.makedirs(LAB_DIR)
    
    if not os.path.exists(EXTERN_DIR):
        os.makedirs(EXTERN_DIR)
    
    if not os.path.exists(TMP_DIR):
        os.makedirs(TMP_DIR)

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

if __name__ == "__main__":
    main()
    