
import click
import git
import os, sys
import requests
from zipfile import ZipFile
import json

@click.command()
@click.option('--output', '-o', help='Output dir')
@click.option('--user', '-u', help='Output dir')
@click.option('--git-url', '-d', help='Git url')
@click.option('--git-user', '-s', help='Git user')
@click.option('--git-pwd', '-w', help='Git password')
@click.option('--raw-db-url', '-r', help='Raw DB url')
@click.option('--sqlite-db-url', '-q', help='Sqlite DB url')
def startup(output, user, git_url, git_user, git_pwd, raw_db_url = None, sqlite_db_url = None):
    print("Starting install in ", output)

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
    for url in settings["git-urls"]:
        git_clone(output, url, git_user, git_pwd)

    # download & extract raw databases
    if not settings.get("biodata-url", None) is None:
        zipfile = os.path.join(output,"./extern/biodata.zip")
        download(settings["biodata-url"], zipfile)
        unzip(zipfile)
        os.remove(zipfile)

    # download sqlite database
    if not settings.get("sqlite-url",None) is None:
        os.mkdir(os.path.join(output,"./app/app-py/data/"))
        zipfile = os.path.join(output,"./app/app-py/data/db.sqlite3.zip")
        download(settings["sqlite-url"], zipfile)
        unzip(zipfile)
        os.remove(zipfile)

def git_clone(output, url, user, pwd):
    print(url)
    repo_group = url.split("/")[-2]
    repo_name = url.split("/")[-1]
    local_path = os.path.join(output, repo_group, repo_name)

    tab = url.split("://")
    url = f"{tab[0]}://{user}:{pwd}@{tab[1]}"

    print("Git clone " + url)
    git.Repo.clone_from(url, local_path, branch='master', depth=1, shallow_submodules=True)
    repo = git.Repo(local_path)
    try:
        for sub in repo.submodules:
            sub_url = sub.config_reader().get_value("url")
            tab = sub_url.split("://")
            sub_url = f"{tab[0]}://{user}:{pwd}@{tab[1]}"
            sub.config_writer().set_value("url", sub_url).release()
            print("Submodule " + sub_url)

        repo.submodule_update(recursive=True)
    except:
        pass

def download(url, filename):
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
    startup()
    