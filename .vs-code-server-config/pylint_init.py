# Script executed in the pylint init hook to add all bricks to the python path

import os
import sys

# Add brick in the bricks folder to the python path
base_dir = "/lab/user/bricks"
for node_name in os.listdir(base_dir):
    brick_path_src = os.path.join(base_dir, node_name, "src")
    if node_name != '.lib' and os.path.exists(brick_path_src):
        sys.path.append(brick_path_src)

# Add brick in the bricks/.lib folder to the python path
base_dir = "/lab/user/bricks/.lib"
for node_name in os.listdir(base_dir):
    brick_path_src = os.path.join(base_dir, node_name, "src")
    if os.path.exists(brick_path_src):
        sys.path.append(brick_path_src)
