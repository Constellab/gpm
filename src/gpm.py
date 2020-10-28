
# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

# Gencovery Package Manager

import click
import git
import os, sys, json
import requests
import json
import subprocess
import shutil
import pip
import urllib
import re

from zipfile import ZipFile

__cdir__ = os.path.dirname(os.path.abspath(__file__))

class GPM():
    git_url = "https://bitbucket.org/gencovery"
    config = []
    structure = ["./bricks", "./data", "./labs", "./logs", "./externs", "./sandbox", "./tmp"]
    _lab_name = "main"
    __is_pulled = []

    def __init__(self, gws_wks="", user_wks="", no_single_branch=None):
        self._read_config()

        if gws_wks != "":
            self.config["gws_wks"] = gws_wks
        
        if user_wks != "":
            self.config["user_wks"] = user_wks

        if not no_single_branch is None:
            if not 'no_single_branch' in self.config:
                self.config["no_single_branch"] = True
        else:
            self.config["no_single_branch"] = no_single_branch

        self._write_config()

    # -- C -- 

    def create_wks_dirs(self, workspace):
        for k in self.structure:
            d = os.path.join(workspace, k)
            if not os.path.exists(d):
                os.makedirs(d)
            #else:
            #    print(f"Path {d} already exists")

    # -- D --

    def download(self, url, dest_dir, dest_filename):
        print(f"Downloading {url} ...")
        dest_file_path = os.path.join(dest_dir,dest_filename)

        if os.path.exists(dest_file_path):
            print(f"Data {dest_file_path} already exists")
            return
        
        
        if dest_file_path.endswith(".zip"):
            if os.path.exists(re.sub(r"\.zip$", "", dest_file_path)):
                print(f"Unzipped data {dest_file_path} already exists")
                return

        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        
        with open(dest_file_path, 'wb') as f:
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

        if dest_file_path.endswith(".zip"):
            self.unzip(dest_file_path)
            os.remove(dest_file_path)

        return dest_file_path

    # -- G --

    def get_gws_wks(self):
        if "gws_wks" in self.config:
            return self.config["gws_wks"]
        else:
            return ""

    def get_user_wks(self):
        if "user_wks" in self.config:
            return self.config["user_wks"]
        else:
            return ""

    def get_repo_dir(self, repo_name):
        file_path = os.path.join(self.get_gws_wks(), "bricks", repo_name)
        if os.path.exists(file_path):
            return file_path, "brick", "gws"

        file_path = os.path.join(self.get_gws_wks(), "externs", repo_name)
        if os.path.exists(file_path):
            return file_path, "externs", "gws"

        file_path = os.path.join(self.get_user_wks(), "bricks", repo_name)
        if os.path.exists(file_path):
            return file_path, "brick", "user"

        file_path = os.path.join(self.get_user_wks(), "labs", repo_name)
        if os.path.exists(file_path):
            return file_path, "lab", "user"

        file_path = os.path.join(self.get_user_wks(), "externs", repo_name)
        if os.path.exists(file_path):
            return file_path, "externs", "user"

        return None, None, None

    # -- I --

    def install_gws(self):
        self.__is_pulled = []
        if self.get_gws_wks().startswith("/"):
            self.create_wks_dirs(self.get_gws_wks())
            self.pull(self.get_gws_wks(), repo_name="all", force=False)

            # pull biota data
            url = self.config["biota_db_url"]
            dest_dir = os.path.join(self.get_gws_wks(), "./data/biota/db/")
            self.download(url, dest_dir, "db.sqlite3.zip")

    def install_user(self):
        self.__is_pulled = []
        if self.get_user_wks().startswith("/"):
            self.create_wks_dirs(self.get_user_wks())
            self.pull(self.get_user_wks(), repo_name="skeleton", force=False)
            self._install_user_lab()

    def _install_user_lab(self):
        skeleton_dir = os.path.join(self.get_user_wks(), "bricks", "skeleton")
        dest_dir = os.path.join(self.get_user_wks(), "labs", self.lab_name)

        if not os.path.exists(dest_dir):
            shutil.move(
                skeleton_dir, 
                dest_dir
            )

            # rename module
            shutil.move(
                os.path.join(dest_dir, "skeleton"), 
                os.path.join(dest_dir, self.lab_name)
            )

            # remove .git folder
            shutil.rmtree(os.path.join(dest_dir, ".git"))

        # update settings.json
        settings_file = os.path.join(dest_dir, "settings.json")
        with open(settings_file, 'r') as f:
            settings = json.load(f)
            settings["type"] = "lab"
            settings["name"] = self.lab_name
            settings["uri"] = self.lab_uri
            settings["host"] = self.lab_host
            settings["virtual_host"] = self.lab_virtual_host
            settings["app"]["title"] = self.lab_title
            settings["app"]["description"] = self.lab_description
            
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=4)

        #replace all words 'skeleton' in settings.json
        with open(settings_file, 'r') as f:
            text = f.read()
            text = text.replace("skeleton", self.lab_name)

        with open(settings_file, 'w') as f:
            f.write(text)

        #replace all words 'skeleton' in app.py
        app_file = os.path.join(dest_dir, self.lab_name, "./app.py")
        with open(app_file, 'r') as f:
            text = f.read()
            text = text.replace("skeleton", self.lab_name)

        with open(app_file, 'w') as f:
            f.write(text)

    def read_repo_type(self, repo_dir="", repo_name=""):
        if repo_dir != "":
            settings_file = os.path.join(repo_dir, "./settings.json")
        elif repo_name != "":
            repo_dir = self.get_repo_dir(repo_name)
            settings_file = os.path.join(repo_dir, "./settings.json")
        else:
            raise Exception("The repo_name or repo_dir is required")

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

    # -- L --

    @property
    def lab_uri(self):
        return self.config["lab"].get("uri", "")

    @property
    def lab_name(self):
        return self.config["lab"].get("name", "main")

    @property
    def lab_title(self):
        return self.config["lab"].get("title", "")

    @property
    def lab_description(self):
        return self.config["lab"].get("description", "")

    @property
    def lab_start_mode(self):
        return self.config["lab"].get("start_mode", "prod")

    @property
    def lab_host(self):
         return self.config["lab"].get("host", "0.0.0.0")

    @property
    def lab_virtual_host(self):
         return self.config["lab"].get("virtual_host", "astro.lab.gencovery.com")

    @property
    def lab_token(self):
        return self.config["lab"].get("token", "")

    # -- R --

    def _read_config(self):
        with open( self.config_file_path, 'r') as f:
            try:
                self.config = json.load(f)
                return
            except:
                raise Exception("Cannot parse the config file. Please check file config file.")
        
        raise Exception("Cannot open the config file")
    
    # -- P -- 

    @property
    def packages(self):
        return self.config["bricks"]

    def pull(self, workspace_dir, repo_name="all", origin=None, username="", userpwd="", force=False):
        if origin == None:
            origin = self.git_url

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
                import _crypt
                git_pwd = _crypt.encrypt_message(git_pwd)
                private["git"]["password"] = git_pwd
                with open(private_file, 'w') as f:
                    json.dump(private, f, indent=4)
            else:
                import _crypt
                _git_pwd = _crypt.decrypt_message(git_pwd)
                git_pwd = ""
                for i in range(0, len(_git_pwd), 2):
                    git_pwd = git_pwd + _git_pwd[i]

        os.environ['GIT_ASKPASS'] = os.path.join(__cdir__,'askpass.sh')
        os.environ['GIT_USERNAME'] = git_user
        os.environ['GIT_PASSWORD'] = git_pwd

        git_pwd = urllib.parse.quote(git_pwd)
        
        if repo_name == "all":
            repos = self.packages
        else:
            repos = [ repo_name ]
        
        for repo_name in repos:
            self._pull_repo(workspace_dir, repo_name, git_user, git_pwd, origin, force)
            self.__is_pulled.append(repo_name)

            # pull sub repos
            repo_dir, _, _ = self.get_repo_dir(repo_name)
            settings_file = os.path.join(repo_dir, "./settings.json")
            if os.path.exists(settings_file):
                with open(settings_file) as f:
                    try:
                        settings = json.load(f)
                        deps = settings.get("dependencies",[]) + settings.get("externs",[])
                        for dep in deps:
                            #if not self.repo_exists(dep):
                            is_already_pulled = (dep in self.__is_pulled)
                            if not is_already_pulled:
                                self.pull(workspace_dir, repo_name=dep, origin=origin, username=git_user, userpwd=git_pwd, force=force)

                    except:
                        pass


    def _pull_repo(self, workspace_dir, repo_name, user, pwd, origin, force):
        url = origin + "/" + repo_name.strip("/") + ".git"

        tab = url.split("://")
        url = f"{tab[0]}://{user}:{pwd}@{tab[1]}"
        #url = f"{tab[0]}://{user}@{tab[1]}"

        repo_dir, repo_type, wk = self.get_repo_dir(repo_name)
        alredy_exists = not repo_dir is None
        if alredy_exists:
            #if force:            
            print(f"Git update {repo_type} {repo_name} (in {wk}) from {tab[0]}://{tab[1]}")
            git_repo = git.Repo(repo_dir)
            o = git_repo.remotes.origin
            o.pull()
        else:
            print(f"Git clone {repo_name} from {tab[0]}://{tab[1]}")
            tmp_repo_dir = os.path.join(workspace_dir, "tmp", repo_name)
            git.Repo.clone_from(
                url, 
                tmp_repo_dir, 
                no_single_branch=self.config["no_single_branch"], 
                depth=1, 
                shallow_submodules=True
            )

            repo_type = self.read_repo_type(repo_dir=tmp_repo_dir)
            if repo_type == "brick":
                repo_dir = os.path.join(workspace_dir, "bricks", repo_name)
            elif repo_type == "lab":
                repo_dir = os.path.join(workspace_dir, "labs", repo_name)
            else:
                repo_dir = os.path.join(workspace_dir, "externs", repo_name)

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

    # -- R --

    def repo_exists(self, repo_name):
        _repo_dir, _, _ = self.get_repo_dir(repo_name)
        return not _repo_dir is None

    # -- S --

    @property
    def config_file_path(self):
        return os.path.join(__cdir__,"../.config.json")
    
    # -- U --

    def unzip(self,filename):
        print(f"Extracting {filename} ..")
        with ZipFile(filename, 'r') as zipObj:
            path = os.path.dirname(filename)
            zipObj.extractall(path)
        print(f"Extraction finished.")

    # -- W --

    def _write_config(self):
        with open(self.config_file_path, 'w') as f:
            try:
                json.dump(self.config, f, indent=4)
            except:
                raise Exception("Cannot parse the config file. Please check file config file.")
    

@click.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True
))
@click.pass_context
@click.option('--install-gws', help='Install gws', required=False, default="")
@click.option('--install-user', help='Install user', required=False, default="")
@click.option('--pull', help='Pull a brick or a lab')
@click.option('--push', help="Push a brick or a lab")
@click.option('--tag', help="Tag name (for push command)")
@click.option('--no-single-branch', is_flag=True, help="Get all git branches")
def main(ctx, install_gws, install_user, pull, push, tag, no_single_branch):
    g = GPM(gws_wks=install_gws, user_wks=install_user, no_single_branch=no_single_branch)

    if install_gws != "":
        g.install_gws()
    
    if install_user != "":
        g.install_user()

    if pull:
        pass

    if push:
        pass


# -- ENTRY POINT --

if __name__ == "__main__":
    main()
    