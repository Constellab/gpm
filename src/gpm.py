
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
import glob

from zipfile import ZipFile

__cdir__ = os.path.dirname(os.path.abspath(__file__))

class GPM():
    default_git_origin = "https://gitea.gencovery.com/gws/"
    default_git_origin_token = DEFAULT_GIT_ORIGIN
    
    config = []
    structure = ["./bricks", "./data", "./main", "./logs", "./externs", "./notebooks", "./tmp"]
    _lab_name = "main"
    __is_pulled = []

    def __init__(self, gws_workspace="", user_workspace="", shallow=None):
        self._read_config()

        if gws_workspace != "":
            self.config["gws_workspace"] = gws_workspace
        
        if user_workspace != "":
            self.config["user_workspace"] = user_workspace

        if shallow is None:
            self.config["shallow"] = self.config.get("shallow", True)
        else:
            self.config["shallow"] = shallow

        self._write_config()

    # -- C -- 

    def create_wks_dirs(self, workspace, skip_main = False):
        for k in self.structure:
            if k == "main" and skip_main:
                continue

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

    def get_gws_workspace(self):
        if "gws_workspace" in self.config:
            return self.config["gws_workspace"]
        else:
            return ""

    def get_user_workspace(self):
        if "user_workspace" in self.config:
            return self.config["user_workspace"]
        else:
            return ""

    def get_repo_dir(self, repo_name):
        file_path = os.path.join(self.get_gws_workspace(), "bricks", repo_name)
        if os.path.exists(file_path):
            return file_path, "brick", "gws"

        file_path = os.path.join(self.get_gws_workspace(), "externs", repo_name)
        if os.path.exists(file_path):
            return file_path, "externs", "gws"

        file_path = os.path.join(self.get_user_workspace(), "bricks", repo_name)
        if os.path.exists(file_path):
            return file_path, "brick", "user"

        file_path = os.path.join(self.get_user_workspace(), "externs", repo_name)
        if os.path.exists(file_path):
            return file_path, "externs", "user"

        return None, None, None

    # -- I --

    def install_gws(self):
        self.__is_pulled = []
        if self.get_gws_workspace().startswith("/"):
            self.create_wks_dirs(self.get_gws_workspace(), skip_main=True)
            repos=self.gws_bricks
            if not repos:
                repos = { "biox": "DEFAULT_GIT_ORIGIN" }
            self.pull(self.get_gws_workspace(), repos=repos, force=False)

            # pull biota data
            url = self.config["urls"]["biota_db"]
            dest_dir = os.path.join(self.get_gws_workspace(), "./data/prod/biota/db/")
            self.download(url, dest_dir, "db.sqlite3.zip")

            #copy notebooks files
            src_files = glob.glob(os.path.join(__cdir__, "../notebooks/**"))
            dest_dir = os.path.join(self.get_gws_workspace(), "./notebooks")
            for src in src_files:
                dst = os.path.join(dest_dir, src.split("/")[-1])
                shutil.copy2(src, dst)

    def install_user(self):
        self.__is_pulled = []
        if self.get_user_workspace().startswith("/"):
            self.create_wks_dirs(self.get_user_workspace(), skip_main=False)
            repos = { 
                "skeleton": "DEFAULT_GIT_ORIGIN", 
                **self.user_bricks 
            }

            self.pull(self.get_user_workspace(), repos=repos, force=False)
            self._install_user_main()

            #copy notebooks files
            src_files = glob.glob(os.path.join(__cdir__, "../notebooks/**"))
            dest_dir = os.path.join(self.get_user_workspace(), "./notebooks")
            for src in src_files:
                dst = os.path.join(dest_dir, src.split("/")[-1])
                shutil.copy2(src, dst)

    def _install_user_main(self):
        skeleton_dir = os.path.join(self.get_user_workspace(), "bricks", "skeleton")
        dest_dir = os.path.join(self.get_user_workspace(), "main", self.lab_name)

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
            settings["name"]                = self.config["lab"].get("name", "main")
            settings["uri"]                 = self.config["lab"].get("uri", "")
            settings["token"]               = self.config["lab"].get("token", "")
            settings["host"]                = self.config["lab"].get("host", "0.0.0.0")
            settings["virtual_host"]        = self.config["lab"].get("virtual_host", "lab.test.gencovery.io")
            
            settings["jlab_token"]          = self.config["lab"].get("jlab_token", "")
            settings["jlab_home_dir"]       = self.config["lab"].get("jlab_home_dir", "")

            settings["central_api_key"]     = self.config["lab"].get("central_api_key", "")
            settings["central_api_url"]     = self.config["lab"].get("central_api_url", "")

            settings["user_uri"]            = self.config["lab"].get("user_uri", "")
            settings["user_email"]          = self.config["lab"].get("user_email", "")
            settings["admin_email"]         = self.config["lab"].get("admin_email", "")

            settings["dependencies"]        = settings.get("dependencies",[]) + \
                                                self.config.get("dependencies",[]).get("gws",[]) + \
                                                self.config.get("dependencies",[]).get("user",[])
            
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
                    #is_lab = settings.get("type", None) == "lab"
                    #if is_lab:
                    #    return "lab"
                    #else:
                    if not settings.get("name", None) is None:
                        return  "brick"
                except:
                    return "extern"
        else:
            return "extern"

    # -- L --

    @property
    def lab_name(self):
        return self.config["lab"].get("name", "main")

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
    def gws_bricks(self) -> dict:
        return self.config["dependencies"].get("gws",{})
    
    @property
    def user_bricks(self) -> dict:
        return self.config["dependencies"].get("user", {})

    def pull(self, workspace_dir, repos={}, username="", userpwd="", force=False):
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
                git_pwd = _crypt.decrypt_message(git_pwd)

        os.environ['GIT_ASKPASS'] = os.path.join(__cdir__,'askpass.sh')
        os.environ['GIT_USERNAME'] = git_user
        os.environ['GIT_PASSWORD'] = git_pwd

        git_pwd = urllib.parse.quote(git_pwd)
        
        for repo_name in repos:
            
            if repos[repo_name]:
                origin = repos[repo_name]
                if origin == self.default_git_origin_token:
                    origin = self.default_git_origin
            else:
                origin = self.default_git_origin
            
            self._pull_repo(workspace_dir, repo_name, git_user, git_pwd, origin, force)
            self.__is_pulled.append(repo_name)

            # pull sub repos
            repo_dir, _, _ = self.get_repo_dir(repo_name)
            settings_file = os.path.join(repo_dir, "./settings.json")
            if os.path.exists(settings_file):
                with open(settings_file) as f:
                    try:
                        settings = json.load(f)

                        # pull bricks
                        deps = settings.get("dependencies",[]) + settings.get("externs",[])
                        for dep in deps:
                            is_already_pulled = (dep in self.__is_pulled)
                            if not is_already_pulled:
                                self.pull(workspace_dir, repos={ dep: origin }, username=git_user, userpwd=git_pwd, force=force)

                        # # pull externs
                        # deps = settings.get("externs",[])
                        # for dep in deps:
                        #     is_already_pulled = (dep in self.__is_pulled)
                        #     if not is_already_pulled:
                        #         self.pull(workspace_dir, repo_names=dep, origin=origin + "/externs", username=git_user, userpwd=git_pwd, force=force)

                    except:
                        pass


    def _pull_repo(self, workspace_dir, repo_name, user, pwd, origin, force):
        url = .strip("/") + "/" + repo_name.strip("/") + ".git"

        tab = url.split("://")
        url = f"{tab[0]}://{user}:{pwd}@{tab[1]}"

        repo_dir, repo_type, wk = self.get_repo_dir(repo_name)
        alredy_exists = not repo_dir is None
        if alredy_exists:
            #if force:            
            print(f"Git update {repo_type} {repo_name} (in {wk}) from {tab[0]}://{tab[1]}")
            git_repo = git.Repo(repo_dir)
            o = git_repo.remotes.origin
            saved_url = o.url
            o.set_url(url)
            o.pull()
            o.set_url(saved_url)
        else:
            print(f"Git clone {repo_name} from {tab[0]}://{tab[1]}")
            tmp_repo_dir = os.path.join(workspace_dir, "tmp", repo_name)
            
            if self.config["git"]["shallow"]:
                git_kwargs = {
                    "depth": 1,
                    "shallow_submodules": True
                }
            else:
                git_kwargs = {}
                
            git.Repo.clone_from(
                url, 
                tmp_repo_dir, 
                **git_kwargs
            )

            repo_type = self.read_repo_type(repo_dir=tmp_repo_dir)
            if repo_type == "brick":
                repo_dir = os.path.join(workspace_dir, "bricks", repo_name)
            elif repo_type == "lab":
                repo_dir = os.path.join(workspace_dir, "main", repo_name)
            else:
                repo_dir = os.path.join(workspace_dir, "externs", repo_name)

            shutil.move(tmp_repo_dir, repo_dir)
            git_repo = git.Repo(repo_dir)

        import re
        try:
            #set submodules pwd
            for sub in git_repo.submodules:
                sub_url = sub.config_reader().get_value("url")
                tab = re.split("://(.+@)?", sub_url)                
                sub_url = f"{tab[0]}://{user}:{pwd}@{tab[2]}" #tab[1] containt hypothetical "login"
                sub.config_writer().set_value("url", sub_url).release()
                print(f"Getting submodule {tab[0]}://{tab[2]}")

            #pull submodules
            git_repo.submodule_update(recursive=True)

            #restore submodule urls
            for sub in git_repo.submodules:
                sub_url = sub.config_reader().get_value("url")
                tab = re.split("://(.+@)?", sub_url)
                sub_url = f"{tab[0]}://{tab[2]}"   #tab[1] containt hypothetical "login"
                sub.config_writer().set_value("url", sub_url).release()

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
@click.option('--gws-workspace', help='GWS workspace dir (absolute path)', required=False, default="")
@click.option('--user-workspace', help='User workspace dir (absolute path)', required=False, default="")
@click.option('--pull', help='Pull a brick or a lab')
@click.option('--push', help="Push a brick or a lab")
@click.option('--tag', help="Tag name (for push command)")
@click.option('--shallow', is_flag=True, help="Get git shallow-code copy if True")
def main(ctx, gws_workspace, user_workspace, pull, push, tag, shallow):
    g = GPM(gws_workspace=gws_workspace, user_workspace=user_workspace, shallow=shallow)

    if gws_workspace != "":
        g.install_gws()
    
    if user_workspace != "":
        g.install_user()

    if pull:
        pass

    if push:
        pass


# -- ENTRY POINT --

if __name__ == "__main__":
    main()
    