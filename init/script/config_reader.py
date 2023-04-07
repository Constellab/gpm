# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com


import json
import os
from typing import TypedDict, Dict, List


class BrickPackage(TypedDict):
    name: str
    version: str


class PipPackage(TypedDict):
    name: str


class PipChanel(TypedDict):
    source: str
    packages: List[PipPackage]


class GitPackage(TypedDict):
    name: str
    version: str
    is_brick: bool  # used for old version, brick are now in bricks


class GitChanel(TypedDict):
    source: str
    packages: List[GitPackage]


class SettingFileEnv(TypedDict):
    bricks: List[BrickPackage]
    git: List[GitChanel]
    pip: List[PipChanel]
    variables: Dict[str, str]


class SettingsFile(TypedDict):
    name: str
    variables: Dict[str, str]
    environment: SettingFileEnv


class PackageInfo(TypedDict):
    """ object containing info to install a git or pip package"""
    name: str
    version: str
    source: str


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

    ################################## Brick ##################################

    def get_brick_packages(self) -> List[BrickPackage]:
        """ Retrieve the list of bricks from bricks section and git and pip old section"""
        bricks: List[BrickPackage] = self.get_environment().get("bricks", [])

        # add bricks from git section
        bricks.extend(self._get_git_packages(is_brick=True))

        return bricks

    ################################## Packages ##################################

    def get_pip_channels(self) -> List[PipChanel]:
        return self.get_environment().get("pip", [])

    def get_git_channels(self) -> List[GitChanel]:
        return self.get_environment().get("git", [])

    def get_pip_packages(self) -> List[PackageInfo]:
        """ Retrieve the list of all packages from git and pip sections"""
        packages: List[PackageInfo] = []

        for pip_channel in self.get_pip_channels():
            for pip_package in pip_channel["packages"]:
                packages.append({
                    "name": pip_package["name"],
                    "version": pip_package.get("version", ''),
                    "source": pip_channel["source"]
                })

        return packages

    def get_git_packages(self) -> List[PackageInfo]:
        return self._get_git_packages(is_brick=False)

    def _get_git_packages(self, is_brick: bool) -> List[PackageInfo]:
        """ Retrieve the list of bricks from git section. This is for old version of config file."""
        bricks: List[PackageInfo] = []

        for git_channel in self.get_git_channels():
            for git_package in git_channel["packages"]:
                if git_package.get("is_brick", False) == is_brick:
                    bricks.append({
                        "name": git_package["name"],
                        "version": git_package.get("version", ''),
                        "source": git_channel["source"]
                    })

        return bricks

    ################################## Other ##################################

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

                return config

            except Exception as err:
                raise Exception("Cannot parse the config file. Please check file config file.") from err
