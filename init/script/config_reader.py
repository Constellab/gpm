# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com


import json
import os
from typing import TypedDict, Dict, List

SKELETON_GIT_ENVIRONMENT = {
    "source": "https://$GWS_GIT_LOGIN:$GWS_GIT_PWD@gitlab.com/gencovery/core",
    "packages": [
        {"name": "skeleton", "version": "", "is_brick": True, "is_hidden": False}
    ]
}

class PipPackage(TypedDict):
  name: str

class PipChanel(TypedDict):
  source: str
  packages: List[PipPackage]

class GitPackage(TypedDict):
  name: str
  version: str
  is_brick: bool

class GitChanel(TypedDict):
  source: str
  packages: List[GitPackage]

class SettingFileEnv(TypedDict):
  git: List[GitChanel]
  pip: List[PipChanel]
  variables: Dict[str, str]

class SettingsFile(TypedDict):
  name: str
  title: str
  description: str
  app_dir: str
  uri: str
  variables: Dict[str, str]
  environment: SettingFileEnv


class SettingsReader:

  settings_file_path: str

  settings: SettingsFile

  def __init__(self, settings_file_path: str):
    self.settings_file_path = settings_file_path
    self.settings = self.read_settings()

  def get_name(self) -> str:
    return self.settings["name"]

  def get_variables(self) -> Dict[str, str]:
    return self.settings["variables"]

  def get_environment(self) -> SettingFileEnv:
    return self.settings.get("environment", {})

  def get_environment_variables(self) -> Dict[str, str]:
    return self.get_environment().get("variables", {})
 
  def get_pip_channels(self) -> List[PipChanel]:
    return self.get_environment().get("pip", [])

  def get_git_channels(self) -> List[GitChanel]:
    return self.get_environment().get("git", [])

  def read_settings(self) -> SettingsFile:
        if not os.path.exists(self.settings_file_path):
            raise Exception(f"Cannot find the config file '{self.settings_file_path}'.")
        with open(self.settings_file_path, 'r', encoding="utf-8") as f:
            try:
                config = json.load(f)
                if not config.get("environment"):
                    config["environment"] = {}
                if not config["environment"].get("git"):
                    config["environment"]["git"] = []

                # Check if skeleton brick exists
                for g in config["environment"]["git"]:
                    if g["source"] == SKELETON_GIT_ENVIRONMENT["source"]:
                        for pkg in g["packages"]:
                            sklt_pkg = SKELETON_GIT_ENVIRONMENT["packages"][0]
                            if pkg["name"] == sklt_pkg["name"]:
                                return config

                # skeleton brick does not exist, add it
                config["environment"]["git"].append(SKELETON_GIT_ENVIRONMENT)
                return config

            except Exception as err:
                raise Exception("Cannot parse the config file. Please check file config file.") from err

  
