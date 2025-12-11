

import os
import subprocess
from unittest import IsolatedAsyncioTestCase

from init.script.config_reader import PackageInfo
from init.script.logger import Logger
from init.script.pip_manager import PipManager


class TestPipManager(IsolatedAsyncioTestCase):

    log_file_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        "test.log"
    )

    def test_pip_manager(self):

        packages: list[PackageInfo] = [{
            'name': 'numpy',
            'version': '1.26.4',
            'source': 'https://pypi.python.org/simple'
        },
            {
            'name': 'pandas',
            'version': '2.2.2',
            'source': 'https://pypi.python.org/simple'
        },
            # simulate a second source
            {
            'name': 'simplejson',
            'version': '3.19.2',
            'source': 'https://pypi.python.org/simple '
        }]

        # Uninstall packages
        packages_to_uninstall = [package['name'] for package in packages]
        cmd = ['pip', 'uninstall'] + packages_to_uninstall + ["-y"]
        subprocess.check_call(cmd)

        logger = Logger(self.log_file_path)

        pip_manager = PipManager(logger, 0, 100, disable_cache=True, log_progress=True)
        pip_manager.add_packages(packages)

        pip_manager.install_packages()
