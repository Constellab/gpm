# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import sys
import os

def activate( brick = "app" ):    
    if 'gws_core' not in sys.modules:
        CORE_LIB_PATH = "/lab/user/bricks/gws_core/src"
        if os.path.exists(CORE_LIB_PATH):
            sys.path.insert(0, CORE_LIB_PATH)
        else:
            raise Exception("Cannot find the core brick")

    from gws_core import runner, manage
    if __name__ == "__main__":
        manage.load_settings("/lab/.sys/app")
        runner.run()