
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
BRICK_DIR = ""
DATA_DIR = ""
LAB_DIR = ""
LOG_DIR = ""
EXTERN_DIR = ""
SANDBOX_DIR = ""
TMP_DIR = ""

PACKAGES = []

@click.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True
))
@click.pass_context
@click.option('--install', is_flag=True, help='Install')
@click.option('--pull', help='Pull a brick')
@click.option('--push', help="Push a brick")

@click.option('--gws-dir', help="GWS workspace directory", required=True)
@click.option('--user-dir', help="User workspace directory", required=True)
@click.option('--lab-name', default="mylab", help='Lab name on install')
@click.option('--no-single-branch', is_flag=True, help="Get all git branches")
def main(ctx, install, pull, push, gws_dir, user_dir, lab_name, no_single_branch):

    if not gws_dir.startswith("/"):
        print("Error: Invalid option '--gws-dir'. Absolute path required.")
        return

    if not user_dir.startswith("/"):
        print("Error: Invalid option '--user_dir'. Absolute path required.")
        return

    if install:
        # pull gws workspace
        _set_cwd(workspace=gws_dir)
        _create_dirs()
        git_pull(repo_name="all", no_single_branch=no_single_branch)
        
        # pull user workspace
        _set_cwd(workspace=user_dir)
        _create_dirs()
        
        # allways create a default lab
        lab_dirs = [f.path for f in os.scandir(LAB_DIR) if f.is_dir()]
        no_lab_exists = (len(lab_dirs) == 0)
        if no_lab_exists:
            _install_skeleton_to_lab(lab_name, gws_dir, user_dir)

    if pull:
        # pull gws workspace
        _set_cwd(workspace=gws_dir)
        git_pull(repo_name=pull, no_single_branch=no_single_branch)

        # pull user workspace
        _set_cwd(workspace=user_dir)
        git_pull(repo_name=pull, no_single_branch=no_single_branch)

    elif push:
        git_push(repo_name=pull)

# -- B --

def _build_repo_url(repo_name, origin=GIT_URL):
    return origin + "/" + repo_name.strip("/") + ".git"

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

def _create_dirs():
    if not os.path.exists(BRICK_DIR):
        os.makedirs(BRICK_DIR)
    else:
        print(f"Path {BRICK_DIR} already exists")

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    if not os.path.exists(LAB_DIR):
        os.makedirs(LAB_DIR)
    
    if not os.path.exists(EXTERN_DIR):
        os.makedirs(EXTERN_DIR)
    
    if not os.path.exists(TMP_DIR):
        os.makedirs(TMP_DIR)

    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    if not os.path.exists(SANDBOX_DIR):
        os.makedirs(SANDBOX_DIR)

# -- D --

def _download(url, filename):
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


# -- G --

def git_pull(repo_name="all", origin=GIT_URL, username="", userpwd="", no_single_branch=True):
    #if origin == GIT_URL:
    git_user = ""
    git_pwd = ""
    private_file = os.path.join(__cdir__, "../.private.json")
    if os.path.exists(private_file):
        with open(private_file, 'r') as f:
            private = json.load(f)
            git_user = private["git"]["login"]
            git_pwd = private["git"]["password"]

    if git_user == "" or git_pwd == "":
        private_file = os.path.join(__cdir__, "../.public.json")
        if os.path.exists(private_file):
            with open(private_file, 'r') as f:
                private = json.load(f)
        else:
            raise Exception("File .public.json not found")

        git_user = private["git"]["login"]
        git_pwd = private["git"]["password"]
        
        
        if not git_pwd:
            raise Exception("The invalid git password")
        elif len(git_pwd) < 64:
            import crypt
            git_pwd = crypt.encrypt_message(git_pwd)
            private["git"]["password"] = git_pwd
            with open(private_file, 'w') as f:
                json.dump(private, f)
        else:
            import crypt
            _git_pwd = crypt.decrypt_message(git_pwd)
            git_pwd = ""
            for i in range(0, len(_git_pwd), 2):
                git_pwd = git_pwd + _git_pwd[i]

    os.environ['GIT_ASKPASS'] = os.path.join(__cdir__,'askpass.sh')
    os.environ['GIT_USERNAME'] = git_user
    os.environ['GIT_PASSWORD'] = git_pwd

    import urllib
    git_pwd = urllib.parse.quote(git_pwd)
    
    PACKAGES = _read_pkgs()

    if repo_name == "all":
        for repo_name in PACKAGES:
            _git_pull_repo(repo_name, git_user, git_pwd, origin, no_single_branch)
    else:
        _git_pull_repo(repo_name, git_user, git_pwd, origin, no_single_branch)

def _git_pull_repo(repo_name, user, pwd, origin=GIT_URL, no_single_branch=True):
    url = _build_repo_url(repo_name, origin)
    tab = url.split("://")
    url = f"{tab[0]}://{user}:{pwd}@{tab[1]}"
    #url = f"{tab[0]}://{user}@{tab[1]}"

    if _is_installed(repo_name):
        print(f"Git update {repo_name} from " + f"{tab[0]}://{tab[1]}")
        
        if _is_installed_brick(repo_name):
            repo_dir = _build_repo_dir_path(repo_name, "brick")
            repo_type_msg = "brick"
        elif _is_installed_lab(repo_name):
            repo_dir = _build_repo_dir_path(repo_name, "lab")
            repo_type_msg = "lab"
        elif _is_installed_extern(repo_name):
            repo_dir = _build_repo_dir_path(repo_name, "extern")
            repo_type_msg = "extern repo"

        print(f"Git update {repo_type_msg} {repo_name} from {tab[0]}://{tab[1]}")
        git_repo = git.Repo(repo_dir)
        o = git_repo.remotes.origin
        o.pull()
    else:
        print(f"Git clone {repo_name} from {tab[0]}://{tab[1]}")
        tmp_repo_dir = _build_tmp_repo_dir_path(repo_name)

        git.Repo.clone_from(
            url, 
            tmp_repo_dir, 
            no_single_branch=no_single_branch, 
            depth=1, 
            shallow_submodules=True
        )

        repo_type = _read_repo_type(tmp_repo_dir)
        repo_dir = _build_repo_dir_path(repo_name, repo_type)

        shutil.move(tmp_repo_dir, repo_dir)
        git_repo = git.Repo(repo_dir)

    try:
        for sub in git_repo.submodules:
            sub_url = sub.config_reader().get_value("url")
            import re
            tab = re.split("://.+@", sub_url)
            sub_url = f"{tab[0]}://{user}:{pwd}@{tab[1]}"
            sub.config_writer().set_value("url", sub_url).release()
            print(f"Getting submodule {tab[0]}://{tab[1]}")

        git_repo.submodule_update(recursive=True)
    except:
        pass

def git_push(repo_name="all", origin=GIT_URL):
    pass

def _git_push_repo(repo_name, user, pwd):
    pass

# -- I --

def _is_installed_brick(repo_name):
    return os.path.exists( _build_repo_dir_path(repo_name,"brick") ) 

def _is_installed_lab(repo_name):
    return os.path.exists( _build_repo_dir_path(repo_name,"lab") ) 

def _is_installed_extern(repo_name):
    return os.path.exists( _build_repo_dir_path(repo_name,"extern") ) 

# -- M --

def _install_skeleton_to_lab(lab_name, gws_dir, user_dir):
    _set_cwd(workspace=gws_dir)
    skeleton_dir = _build_repo_dir_path("skeleton", "brick")

    _set_cwd(workspace=user_dir)
    dest_dir = os.path.join(LAB_DIR, lab_name)
    shutil.copytree(
        skeleton_dir, 
        dest_dir
    )

    # rename module
    shutil.move(
        os.path.join(dest_dir, "skeleton"), 
        os.path.join(dest_dir, lab_name)
    )

    # remove .git folder
    shutil.rmtree(os.path.join(dest_dir, ".git"))

    # update settings.json
    settings_file = os.path.join(dest_dir, "settings.json")
    with open(settings_file, 'r') as f:
        settings = json.load(f)
        settings["type"] = "lab"
        settings["name"] = lab_name
        settings["app"]["title"] = "My lab"
        settings["app"]["description"] = "My lab"
        
    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=4)

    #replace all words 'skeleton' in settings.json
    with open(settings_file, 'r') as f:
        text = f.read()
        text = text.replace("skeleton", lab_name)

    with open(settings_file, 'w') as f:
        f.write(text)

    #replace all words 'skeleton' in app.py
    app_file = os.path.join(dest_dir, lab_name, "./app.py")
    with open(app_file, 'r') as f:
        text = f.read()
        text = text.replace("skeleton", lab_name)

    with open(app_file, 'w') as f:
        f.write(text)

# -- R --

def _read_repo_type(repo_dir):
    settings_file = os.path.join(repo_dir, "settings.json")
    if os.path.exists(settings_file):
        with open(settings_file) as f:
            try:
                settings = json.load(f)
                is_lab = settings.get("type", None) == "lab"
                if is_lab:
                    return "lab"
                else:
                    return  "brick"
            except:
                return "extern"
    else:
        return "extern"

def _read_pkgs():
    with open(os.path.join(__cdir__,"../packages.json")) as f:
            try:
                return json.load(f)
            except:
                raise Exception("Error while parsing the settings JSON file. Please check file setting file.")

# -- S --

def _set_cwd(workspace):
    global BRICK_DIR
    global DATA_DIR
    global LAB_DIR
    global LOG_DIR
    global EXTERN_DIR
    global SANDBOX_DIR
    global TMP_DIR

    BRICK_DIR = os.path.join(workspace, "./bricks")
    DATA_DIR = os.path.join(workspace, "./data")
    LAB_DIR = os.path.join(workspace, "./labs")
    LOG_DIR = os.path.join(workspace, "./logs")
    EXTERN_DIR = os.path.join(workspace, "./externs")
    SANDBOX_DIR = os.path.join(workspace, "./sandbox")
    TMP_DIR = os.path.join(workspace, "./tmp")

# -- U --

def unzip(filename):
    print(f"Extracting {filename} ...")
    with ZipFile(filename, 'r') as zipObj:
        path = os.path.dirname(filename)
        zipObj.extractall(path)
    print(f"Extraction finished.")

# -- ENTRY POINT --

if __name__ == "__main__":
    main()
    