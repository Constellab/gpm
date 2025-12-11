#!/bin/bash
set -e

# mode to create a local dev environment where vscode can log in to the container
bash /init-lab/init_lab.sh CODELAB

# Setup SSH for local dev environment
sudo chown -R labuser:labuser /home/labuser/.ssh

echo "Dev environment is ready."

# prevent docker to stop 
tail -f /dev/null
