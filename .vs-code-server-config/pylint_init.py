# Script executed in the pylint init hook to add all bricks to the python path

import os
import sys

user_bricks_folder = os.path.join('/lab', 'user', 'bricks')
sys_bricks_folder = os.path.join('/lab', '.sys', 'bricks')

# Add brick in the bricks folder to the python path
for node_name in os.listdir(user_bricks_folder):
    brick_path_src = os.path.join(user_bricks_folder, node_name, "src")
    if node_name != '.lib' and os.path.exists(brick_path_src):
        sys.path.append(brick_path_src)

# Add brick in the bricks/.lib folder to the python path
for node_name in os.listdir(sys_bricks_folder):
    brick_path_src = os.path.join(sys_bricks_folder, node_name, "src")
    if os.path.exists(brick_path_src):
        sys.path.append(brick_path_src)
