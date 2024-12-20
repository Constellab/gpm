

import os
import subprocess
from typing import Dict, List

from .logger import Logger
from .config_reader import PackageInfo


class PipManager:
    """ Class to store pip packages to install and install them at the end of the installation process """

    packages: List[PackageInfo] = []

    _installed_packages_version: List[str] = []

    def __init__(self):
        self.packages = []
        self._installed_packages_version = []

    def add_packages(self, packages: List[PackageInfo]) -> None:
        """ Add a list of packages to the list of packages to install """

        for package in packages:
            self.add_package(package)

    def add_package(self, package: PackageInfo) -> None:
        """ Add a package to the list of packages to install """

        # check if package is already in the list
        if not any([package["name"] == p["name"] for p in self.packages]):
            self.packages.append(package)

    def install_packages(self) -> None:
        """ Install all packages in the list """

        # group packages by source
        packages_by_source: Dict[str, List[PackageInfo]] = {}

        for package in self.packages:
            if package["source"] not in packages_by_source:
                packages_by_source[package["source"]] = []

            packages_by_source[package["source"]].append(package)

        # install packages by source
        for source, packages in packages_by_source.items():
            self._install_packages_for_source(source, packages)

    def _install_packages_for_source(self, source: str, packages: List[PackageInfo]) -> None:
        """ Install all packages for a given source """

        _packages_with_version: List[str] = []

        for package in packages:
            name = package['name']
            version = package.get('version', '')
            if version:
                if version[0] not in [">", "<", "="]:
                    version = "==" + version
            _packages_with_version.append(f"{name}{version}")

        if not _packages_with_version:
            return

        _packages_with_version.sort()

        cmd = ["python3", "-m", "pip", "install", *
               _packages_with_version, "--extra-index-url", source]
        Logger.info(f"Installing pip packages : '{' '.join(cmd)}'")
        self._run_proc(cmd)

        self._installed_packages_version.extend(_packages_with_version)

        Logger.info("Pip packages successfully insalled")

    def _run_proc(self, cmd, cwd=None) -> bool:
        if cwd:
            if not os.path.exists(cwd):
                os.makedirs(cwd)
        try:
            subprocess.check_call(cmd, cwd=cwd)
            return True
        except Exception as err:
            Logger.error("Error during pip instalation")
            raise err

    def get_installed_packages_version(self) -> List[str]:
        packages = self._installed_packages_version
        packages.sort()
        return packages
