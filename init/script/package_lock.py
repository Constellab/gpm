# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from typing import List, Literal, TypedDict, Optional


class InstalledPackage(TypedDict):
    name: str
    version: str
    is_brick: bool
    type: Literal["pip", "git"]

    # if brick, tells if the brick is hidden
    is_hidden: bool

    # if git, the hash of the commit
    git_hash: Optional[str]

    path: str

class PackageLock():

    packages: List[InstalledPackage]

    def __init__(self):
        self.packages = []

    def add_package(self, package: InstalledPackage):
        self.packages.append(package)


    def is_installed(self, package_name: str) -> bool:
        for package in self.packages:
            if package["name"] == package_name:
                return True
        return False

    def add_git_package(self, name: str, version: str, git_hash: str, path: str):
        self.add_package({
            "name": name,
            "version": version,
            "is_brick": False,
            "type": "git",
            "is_hidden": None,
            "git_hash": git_hash,
            "path": path
        })

    def add_pip_package(self, name: str, version: str, path: str):
        self.add_package({
            "name": name,
            "version": version,
            "is_brick": False,
            "type": "pip",
            "is_hidden": None,
            "git_hash": None,
            "path": path
        })

    def add_brick_git_package(self, name: str, version: str, is_hidden: bool, path: str):
        self.add_package({
            "name": name,
            "version": version,
            "is_brick": True,
            "type": "git",
            "is_hidden": is_hidden,
            "git_hash": None,
            "path": path
        })

    def add_brick_pip_package(self, name: str, version: str, is_hidden: bool, path: str):
        self.add_package({
            "name": name,
            "version": version,
            "is_brick": True,
            "type": "pip",
            "is_hidden": is_hidden,
            "git_hash": None,
            "path": path
        })

