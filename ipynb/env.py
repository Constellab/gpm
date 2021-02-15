# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import sys
import os

def activate( brick = "main" ):
    __cdir__ = os.path.dirname(os.path.abspath(__file__))
    
    # activate gws
    def set_path(rel_gws_path):
        for _ in range(0,10):
            rel_gws_path = os.path.join("../", rel_gws_path)
            abs_gws_path = os.path.join(__cdir__, rel_gws_path)
            if os.path.exists(abs_gws_path):
                sys.path.append(abs_gws_path)
                return True
    is_set =  set_path("./.gws/bricks/gws") or set_path("./gws/bricks/gws")
    if not is_set:
        raise Exception("Cannot find the base gws brick")
    
    if brick == "main":
        __brick_dir__ = os.path.join(__cdir__, f"../main/{brick}")
    else:
        __brick_dir__ = os.path.join(__cdir__, f"../bricks/{brick}")
    
    if not os.path.exists(__brick_dir__):
        raise Exception(f"Could not activate the lab")
    
    from gws.manage import load_settings
    load_settings(__brick_dir__)
    
    # activate local db
    from gws.settings import Settings
    settings = Settings.retrieve()
    settings.data["db_name"] = os.path.join(__cdir__, "test_db.sqlite3")
    settings.data["is_test"] = True        
    settings.data["prod_biota_db"] = True
    settings.save()
    
    # return current dir
    return __cdir__
