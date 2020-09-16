
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

@click.command()
@click.option('--pull', help='Install')
@click.option('--appdir', help='App dir')
@click.option('--datadir', help='Data dir')
def main(pull=False, push=False, appdir=False, datadir=False):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, "private.json")) as f:
        data = json.load(f)
        user = data["git_crenditals"]["user"]
        pwd = data["git_crenditals"]["password"]
        if pull:
            repo = pull
            pull(appdir, datadir, user, pwd, repo=repo)
        elif push:
            pass

def pull(appdir, datadir, git_user, git_pwd, repo="all"):
    print("Installing in ", appdir)

    __cdir__ = os.path.dirname(os.path.abspath(__file__))
    os.environ['GIT_ASKPASS'] = os.path.join(__cdir__,'askpass.sh')
    os.environ['GIT_USERNAME'] = git_user
    os.environ['GIT_PASSWORD'] = git_pwd

    with open(os.path.join(__cdir__,"settings.json")) as f:
        try:
            settings = json.load(f)
        except:
            raise Exception("Error while parsing the settings JSON file. Please check file setting file.")

    # git_clone gws
    if repo == "all":
        for repo_loc in settings["git-repo"]:
            git_url = "https://gitea.gencovery.com"
            url = git_url + "/" + repo_loc.strip("/")
            git_clone(appdir, url, git_user, git_pwd)
    else:
        repo_loc = settings["git-repo"][repo]
        git_url = "https://gitea.gencovery.com"
        url = git_url + "/" + repo_loc.strip("/")
        git_clone(appdir, url, git_user, git_pwd)

    # download & extract raw databases
    if not settings.get("biodata-raw", None) is None:
        zipfile = os.path.join(datadir,"./biota/biodata.zip")
        download(settings["biodata-raw"], zipfile)
        unzip(zipfile)
        os.remove(zipfile)

    # download sqlite database
    if not settings.get("biodata-sqlite",None) is None:
        os.mkdir(os.path.join(datadir,"./biota/"))
        zipfile = os.path.join(datadir,"./biota/db.sqlite3.zip")
        download(settings["biodata-sqlite"], zipfile)
        unzip(zipfile)
        os.remove(zipfile)

def git_clone(appdir, url, user, pwd):
    print(url)
    repo_group = url.split("/")[-2]
    repo_name = url.split("/")[-1]
    local_path = os.path.join(appdir, repo_group, repo_name)

    tab = url.split("://")
    url = f"{tab[0]}://{user}:{pwd}@{tab[1]}"

    #print("Git clone " + url)
    print("Git clone " + f"{tab[0]}://{tab[1]}")

    git.Repo.clone_from(url, local_path, branch='master', depth=1, shallow_submodules=True)
    repo = git.Repo(local_path)
    try:
        for sub in repo.submodules:
            sub_url = sub.config_reader().get_value("url")
            tab = sub_url.split("://")
            sub_url = f"{tab[0]}://{user}:{pwd}@{tab[1]}"
            sub.config_writer().set_value("url", sub_url).release()
            #print("Submodule " + sub_url)
            print("Submodule " + f"{tab[0]}://{tab[1]}")

        repo.submodule_update(recursive=True)
    except:
        pass
    
    req_file = os.path.join(local_path, "requirements.txt")
    if os.path.exists(req_file):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file])
        except:
            pass

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
    