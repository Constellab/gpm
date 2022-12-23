# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import json
import os
import shutil
import subprocess
from unittest import IsolatedAsyncioTestCase
from init.script.config_reader import SettingsReader
from init.script.gpm import GPM, BrickInstalationInfo
import importlib

GENCOVERY_CORE_REPO="https://$GWS_GIT_LOGIN:$GWS_GIT_PWD@gitlab.com/gencovery/core/gws_core.git"
GWS_CORE_VERSION="0.2.1"


class TestGpm(IsolatedAsyncioTestCase):

    def test_glab(self):


      subprocess.run(["pip", "uninstall", 'pronto', "-y"])
       # Check that pronto is not installed
      self.assertIsNone(importlib.find_loader('pronto'))


      __cdir__ = os.path.dirname(os.path.abspath(__file__))
      GPM.LAB_WORKSPACE_DIR = os.path.join(__cdir__, "tests/build/lab")
      GPM.CONFIG_FILE_PATH = os.path.join(__cdir__, "tests/config.json")

      # clean up the workspace
      if os.path.exists(GPM.LAB_WORKSPACE_DIR):
        shutil.rmtree(GPM.LAB_WORKSPACE_DIR, ignore_errors=True)
      
      gpm = GPM(settings_file_path=GPM.CONFIG_FILE_PATH, env_mode='GLAB')


      gpm.init_all()

      # check that gws_core was cloned
      gws_core_brick_path = os.path.join(gpm.get_hidden_brick_dir(), "gws_core")
      gws_core_settings_path = os.path.join(gws_core_brick_path, "settings.json")
      self.assertTrue(os.path.exists(gws_core_settings_path))
      
      # check that gws_biota was cloned
      gws_biota_brick_path = os.path.join(gpm.get_hidden_brick_dir(), "gws_biota")
      gws_biota_settings_path = os.path.join(gws_biota_brick_path, "settings.json")
      self.assertTrue(os.path.exists(gws_biota_settings_path))
      
      # check that skeleton was cloned
      skeleton_brick_path = os.path.join(gpm.get_hidden_brick_dir(), "skeleton")
      skeleton_settings_path = os.path.join(skeleton_brick_path, "settings.json")
      self.assertTrue(os.path.exists(skeleton_settings_path))
    
      # check that brendapy was cloned
      brendapy_readme_path = os.path.join(gpm.get_external_lib_dir(), "brendapy", "README.md")
      self.assertTrue(os.path.exists(brendapy_readme_path))

      # Check that pip dependecies of biota are installed
      self.assertIsNotNone(importlib.find_loader('pronto'))

      # Check that the information file is created
      info_file_path = os.path.join(gws_core_brick_path,GPM.BRICK_INSTALLATION_FILE)
      self.assertTrue(os.path.exists(info_file_path))
      with open(info_file_path, 'r') as f:
        info: BrickInstalationInfo = json.load(f)
        self.assertEqual(info['version'], GWS_CORE_VERSION)
        self.assertEqual(info['name'], "gws_core")
        # check that gws_core was installed because of gws_biota dependency
        self.assertEqual(info['parent_name'], "gws_biota")
        self.assertTrue(len(info['git_hash']) > 0)
        self.assertTrue(len(info['created_at']) > 0)


      # Check that the update for hide brick works
      # to do this, delete the settings.json file and update the brick, 
      # check if the settings.json file is created
      readme = os.path.join(gws_core_brick_path, "README.md")
      os.remove(readme)
      self.assertFalse(os.path.exists(readme))
      gpm.install_brick_git_package("gws_core", "0.2.1", GENCOVERY_CORE_REPO, 'app')
      self.assertTrue(os.path.exists(readme))


      # test other methods
      brick_list = gpm.list_all_brick_paths()
      self.assertEqual(len(brick_list), 3)
      self.assertTrue(gws_core_brick_path in brick_list)
      self.assertTrue(gws_biota_brick_path in brick_list)
      self.assertTrue(skeleton_brick_path in brick_list)


      # Check the app start is well configured
      sys_app_path = os.path.join(GPM.SYS_WORKSPACE_DIR, "app")
      self.assertTrue(os.path.exists(sys_app_path))
      self.assertTrue(os.path.exists(os.path.join(sys_app_path, "settings.json")))
      self.assertTrue(os.path.exists(os.path.join(sys_app_path, "manage.py")))

      setting_reader = SettingsReader(os.path.join(sys_app_path, "settings.json"))
      # check that the skeleton and gws_biota are listed
      chanel = setting_reader.get_git_channels()[0]
      self.assertEqual(len([x for x in chanel["packages"] if x["name"] == "gws_biota"]), 1)
      self.assertEqual(len([x for x in chanel["packages"] if x["name"] == "skeleton"]), 1)
      
     
   
    def test_codelab(self):

      __cdir__ = os.path.dirname(os.path.abspath(__file__))
      GPM.LAB_WORKSPACE_DIR = os.path.join(__cdir__, "tests/build/lab")
      GPM.CONFIG_FILE_PATH = os.path.join(__cdir__, "tests/config.json")
      GPM.VS_CODE_DEFAULT_CONFIG_PATH = os.path.join(__cdir__, ".vs-code-server-config")

      # clean up the workspace
      if os.path.exists(GPM.LAB_WORKSPACE_DIR):
        shutil.rmtree(GPM.LAB_WORKSPACE_DIR, ignore_errors=True)
      
      gpm = GPM(settings_file_path=GPM.CONFIG_FILE_PATH, env_mode='CODELAB')


      gpm.init_all()

      # check that all the vscode config file are created
      self.assertTrue(os.path.exists(gpm.get_vs_code_setting_file_path()))
      self.assertTrue(os.path.exists(os.path.join(gpm.get_vs_code_setting_folder(), 'extensions.json')))
      self.assertTrue(os.path.exists(os.path.join(gpm.get_vs_code_setting_folder(), 'launch.json')))
      self.assertTrue(os.path.exists(os.path.join(gpm.USER_WORKSPACE_DIR, '.pylintrc')))
      self.assertTrue(os.path.exists(os.path.join(gpm.USER_WORKSPACE_DIR, 'pylint_init.py')))

      with open(gpm.get_vs_code_setting_file_path(), 'r') as f:
              # load json file 
              settings = json.load(f)

              self.assertTrue(os.path.join(gpm.get_hidden_brick_dir(), 'gws_core', 'src') in settings['python.autoComplete.extraPaths'])
              self.assertTrue(os.path.join(gpm.get_hidden_brick_dir(), 'gws_biota', 'src') in settings['python.autoComplete.extraPaths'])
              self.assertTrue(os.path.join(gpm.get_hidden_brick_dir(), 'skeleton', 'src') in settings['python.autoComplete.extraPaths'])

     
      # test to move the brick to non hidden folder
      gws_core_path = os.path.join(gpm.get_hidden_brick_dir(), 'gws_core')
      gws_core_dest_path = os.path.join(gpm.get_user_brick_dir(), 'gws_core')

      shutil.move(gws_core_path, gws_core_dest_path)
      # delete the reamdme file to force the update
      readme = os.path.join(gws_core_dest_path, "README.md")
      os.remove(readme)
      self.assertFalse(os.path.exists(readme))
      # re-install gws_core but as it is in the user brick folder, it should not be updated
      gpm.install_brick_git_package("gws_core", "0.2.1", GENCOVERY_CORE_REPO, 'app')
      self.assertFalse(os.path.exists(readme))