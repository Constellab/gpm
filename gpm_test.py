# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import os
import shutil
from unittest import IsolatedAsyncioTestCase

from gpm import GPM

GENCOVERY_CORE_REPO="https://$GWS_GIT_LOGIN:$GWS_GIT_PWD@gitlab.com/gencovery/core/gws_core.git"
GWS_CORE_VERSION="0.2.1"


class TestGpm(IsolatedAsyncioTestCase):

    def test_gpm(self):
      __cdir__ = os.path.dirname(os.path.abspath(__file__))
      GPM.LAB_WORKSPACE_DIR = os.path.join(__cdir__, "./tests/build/lab")
      GPM.CONFIG_FILE_PATH = os.path.join(__cdir__, "./tests/config.json")

      # clean up the workspace
      if os.path.exists(GPM.LAB_WORKSPACE_DIR):
        shutil.rmtree(GPM.LAB_WORKSPACE_DIR, ignore_errors=True)
      
      gpm = GPM(settings_file_path=GPM.CONFIG_FILE_PATH)


      gpm.is_test = True
      gpm.install_pip_and_git_packages()
      gpm.install_app_entrypoint()
      gpm.install_notebook_entrypoint()

      # check that gws_core was cloned
      gws_core_settings_path = os.path.join(gpm.get_hidden_brick_dir(), "gws_core", "settings.json")
      self.assertTrue(os.path.exists(gws_core_settings_path))
      
      # check that gws_biota was cloned
      gws_biota_settings_path = os.path.join(gpm.get_hidden_brick_dir(), "gws_biota", "settings.json")
      self.assertTrue(os.path.exists(gws_biota_settings_path))
      
      # check that skeleton was cloned
      skeleton_settings_path = os.path.join(gpm.get_hidden_brick_dir(), "skeleton", "settings.json")
      self.assertTrue(os.path.exists(skeleton_settings_path))
    
      # check that brendapy was cloned
      brendapy_readme_path = os.path.join(gpm.get_external_lib_dir(), "brendapy", "README.md")
      self.assertTrue(os.path.exists(brendapy_readme_path))

      # Check that the update for hide brick works
      # to do this, delete the settings.json file and update the brick, 
      # check if the settings.json file is created
      os.remove(gws_core_settings_path)
      self.assertFalse(os.path.exists(gws_core_settings_path))
      gpm.install_brick_git_package("gws_core", "0.2.1", GENCOVERY_CORE_REPO)
      self.assertTrue(os.path.exists(gws_core_settings_path))


   