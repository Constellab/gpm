import select
import subprocess

from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import InvalidVersion, Version

from .config_reader import PackageInfo, TrackedPackageInfo
from .logger import Logger


class PipManager:
    """Class to store pip packages to install and install them at the end of the installation process"""

    packages: list[TrackedPackageInfo]

    _installed_packages_version: list[str]

    logger: Logger

    # values to normalize the PipManager progress to the global progress
    global_progress_start: float
    global_progress_end: float

    # current step of the pip manager
    # from 0 to 100 based on pip manager progress
    current_progress: float
    download_finished: bool

    disable_cache: bool
    log_progress: bool

    PROGRESS_TEXT: str = "Installing bricks dependencies"
    # The message indicating that a package is being downloaded is formatted as follows:
    # "Downloading pandas-2.2.2*"
    DOWNLOADING_PACKAGE_TEXT: str = "Downloading "

    # we consider the downloads takes 80% and installation takes 20% of the progress
    DOWLOADING_END_TEXT: str = "Installing collected packages"
    DOWNLOADING_END_PROGRESS: float = 80.0

    # Number of lines in the log for a package to be considered as downloaded
    NUMBER_OF_PACKAGE_LOG_LINES: int = 2

    def __init__(
        self,
        logger: Logger,
        global_progress_start: float,
        global_progress_end: float,
        disable_cache: bool = False,
        log_progress: bool = False,
    ) -> None:
        self.packages = []
        self._installed_packages_version = []
        self.logger = logger
        self.global_progress_start = global_progress_start
        self.global_progress_end = global_progress_end
        self.disable_cache = disable_cache
        self.log_progress = log_progress
        self.current_progress = 0.0
        self.download_finished = False

    def add_packages(self, packages: list[PackageInfo], brick_name: str) -> None:
        """Add a list of packages to the list of packages to install"""

        for package in packages:
            self.add_package(package, brick_name)

    def add_package(self, package: PackageInfo, brick_name: str) -> None:
        """Add a package to the list of packages to install.

        Note: Packages are added without conflict checking.
        Call check_conflicts() before install_packages() to validate.
        """
        tracked = TrackedPackageInfo(
            name=package.name,
            version=package.version,
            source=package.source,
            brick_name=brick_name,
        )
        self.packages.append(tracked)

    @staticmethod
    def _is_pinned_version(version: str) -> bool:
        """Check if a version string is a pinned version (no operators)."""
        if not version:
            return False
        return version[0] not in (">", "<", "=", "~", "!")

    @staticmethod
    def _versions_compatible(v1: str, v2: str) -> bool:
        """Check if two version specifications are compatible.

        Cases:
        - Both pinned: compatible only if equal
        - One pinned, one range: compatible if pinned version satisfies the range
        - Both ranges: assume compatible (let pip resolve at install time)
        - Either empty: assume compatible
        """
        if not v1 or not v2:
            return True

        v1_pinned = PipManager._is_pinned_version(v1)
        v2_pinned = PipManager._is_pinned_version(v2)

        try:
            if v1_pinned and v2_pinned:
                return Version(v1) == Version(v2)
            if v1_pinned and not v2_pinned:
                return Version(v1) in SpecifierSet(v2)
            if not v1_pinned and v2_pinned:
                return Version(v2) in SpecifierSet(v1)
            # Both are ranges — assume compatible, let pip resolve
            return True
        except (InvalidVersion, InvalidSpecifier):
            # If we can't parse, fall back to string comparison
            return v1 == v2

    def check_conflicts(self) -> None:
        """Check for version conflicts in the package list.

        Raises an Exception if conflicts are detected.
        Logs all conflicts before raising.
        """
        # Group packages by name to find duplicates
        packages_by_name: dict[str, list[TrackedPackageInfo]] = {}
        for package in self.packages:
            if package.name not in packages_by_name:
                packages_by_name[package.name] = []
            packages_by_name[package.name].append(package)

        # Find conflicts: check pairwise version compatibility
        conflicts: list[tuple[str, list[TrackedPackageInfo]]] = []
        for package_name, package_list in packages_by_name.items():
            if len(package_list) > 1:
                has_conflict = False
                for i in range(len(package_list)):
                    for j in range(i + 1, len(package_list)):
                        if not self._versions_compatible(
                            package_list[i].version, package_list[j].version
                        ):
                            has_conflict = True
                            break
                    if has_conflict:
                        break
                if has_conflict:
                    conflicts.append((package_name, package_list))

        # If conflicts found, log them all and raise error
        if conflicts:
            self.logger.error("Package version conflicts detected:")
            for package_name, package_list in conflicts:
                brick_details = ", ".join(
                    f"brick '{pkg.brick_name}' requires '{pkg.version or '(no version)'}'"
                    for pkg in package_list
                )
                self.logger.error(f"  - '{package_name}': {brick_details}")

            self.logger.error("")
            self.logger.error(
                "To resolve conflicts, consider using version ranges (e.g., '>=2.31.0,<3.0.0') "
                "instead of pinned versions in your brick settings.json files."
            )
            self.logger.error("See DEPENDENCY_MANAGEMENT.md for more information.")

            raise Exception(
                f"Found {len(conflicts)} package(s) with version conflicts. "
                f"Please resolve the conflicts before continuing."
            )

        self.logger.info(
            f"No package conflicts detected. {len(packages_by_name)} unique packages to install."
        )

    def install_packages(self) -> None:
        """Install all packages in the list.

        Automatically checks for conflicts before installation.
        """
        # Check for conflicts before installing
        self.check_conflicts()

        # Deduplicate packages (keep first occurrence of each unique package name+version)
        seen = set()
        deduplicated_packages = []
        for package in self.packages:
            key = (package.name, package.version)
            if key not in seen:
                seen.add(key)
                deduplicated_packages.append(package)

        # reset the progress
        self.current_progress = 0.0

        # group packages by source
        packages_by_source: dict[str, list[TrackedPackageInfo]] = {}

        for package in deduplicated_packages:
            if package.source not in packages_by_source:
                packages_by_source[package.source] = []

            packages_by_source[package.source].append(package)

        # install packages by source
        for source, packages in packages_by_source.items():
            self._install_packages_for_source(source, packages)

    def _install_packages_for_source(self, source: str, packages: list[TrackedPackageInfo]) -> None:
        """Install all packages for a given source"""

        _packages_with_version: list[str] = []

        for package in packages:
            name = package.name
            version = package.version
            # Only add == prefix if version doesn't already have a comparator
            # This supports both pinned versions (2.31.0) and ranges (>=2.31.0,<3.0.0)
            if version and version[0] not in [">", "<", "=", "~", "!"]:
                version = "==" + version
            _packages_with_version.append(f"{name}{version}")

        if not _packages_with_version:
            return

        _packages_with_version.sort()

        cmd = [
            "python3",
            "-m",
            "pip",
            "install",
            *_packages_with_version,
            "--extra-index-url",
            source.strip(),
        ]

        if self.disable_cache:
            cmd.append("--no-cache-dir")

        # Format command with packages wrapped in quotes
        cmd_parts = cmd[:4]  # python3 -m pip install
        quoted_packages = [f'"{pkg}"' for pkg in _packages_with_version]
        cmd_parts.extend(quoted_packages)
        cmd_parts.extend(cmd[4 + len(_packages_with_version) :])  # --extra-index-url and source
        self.logger.info(f"Installing pip packages : '{' '.join(cmd_parts)}'")

        self._run_cmd(cmd, package_count=len(packages))

        self._installed_packages_version.extend(_packages_with_version)

        self.logger.info("Pip packages successfully installed")

    def _run_cmd(self, cmd: list[str], package_count: int) -> bool:
        self.download_finished = False

        # set the install ratio if there is multiple source, multiple install commands are trigger
        install_ratio = package_count / len(self.packages)

      
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        reads = [proc.stdout.fileno(), proc.stderr.fileno()]
        while True:
            # return the list of file descriptors that are ready to be read
            ret = select.select(reads, [], [])

            has_read: bool = False

            for file_no in ret[0]:
                if file_no == proc.stdout.fileno():
                    read = proc.stdout.readline()
                    if read:
                        self._handle_output(read.decode("utf-8"), install_ratio, package_count)
                        has_read = True
                elif file_no == proc.stderr.fileno():
                    read = proc.stderr.readline()
                    if read:
                        self.logger.error(read.decode("utf-8"))
                        has_read = True

            poll = proc.poll()

            # stop if the process has finished and there is no more data to read
            # we need to check if there is no more data to read because the process can be finished but there is still data in the buffer (if long log at the end)
            if poll is not None and not has_read:
                break

        # Check if pip command succeeded
        if proc.returncode != 0:
            error_msg = f"Pip installation failed with exit code {proc.returncode}. Check the error logs for details."
            raise Exception(error_msg)

        return True
       
    def _handle_output(self, output: str, install_ratio: float, package_count: int) -> None:
        self.logger.info(output)

        if self.download_finished:
            return

        output = output.strip()
        # if we detect the step end text, we move to the next step
        if output.startswith(self.DOWLOADING_END_TEXT):
            # we add the remaining progress to reach 100%
            add_progress = (100 - self.DOWNLOADING_END_PROGRESS) * install_ratio
            self._update_progress(add_progress)
            self.download_finished = True
            return

        # if we detect the line of a package, we update the progress
        if output.startswith(self.DOWNLOADING_PACKAGE_TEXT):
            # get the text after "Downloading "
            after_text = output[len(self.DOWNLOADING_PACKAGE_TEXT) :]

            # if the text after is one of the package name, we update the progress
            for package in self.packages:
                if after_text.startswith(package.name):
                    # number of line to consider all package as downloaded
                    total_required_lines = package_count * self.NUMBER_OF_PACKAGE_LOG_LINES
                    # When we rach the last package downloaded, the progress should be at 80%
                    downloaded_package_ratio = self.DOWNLOADING_END_PROGRESS / 100

                    # we get the percentage of 1 package of the total number of packages
                    # then we apply the different ratio to get the progress
                    add_progress = (
                        (1 / (total_required_lines))
                        * 100
                        * downloaded_package_ratio
                        * install_ratio
                    )

                    self._update_progress(add_progress)
                    return

    def _update_progress(self, progress_add: float) -> None:
        self.current_progress += progress_add
        # normalise progress base on global_progress_start and global_progress_end
        normalized_progress = self._normalize_progress(
            self.current_progress, self.global_progress_start, self.global_progress_end
        )
        # we skip the log print to avoid polluting the logs
        self.logger.log_progress(
            self.PROGRESS_TEXT, int(normalized_progress), log_in_console=self.log_progress
        )

    def _normalize_progress(
        self, progress: float, progress_start: float, progress_end: float
    ) -> float:
        return progress_start + ((progress / 100) * (progress_end - progress_start))

    def get_installed_packages_version(self) -> list[str]:
        packages = self._installed_packages_version
        packages.sort()
        return packages
