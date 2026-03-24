#!/bin/bash
set -e

# Run SSH init as root (requires sudo since entrypoint may run as labuser)
# Use sudo -E to preserve all environment variables
sudo -E bash /init-lab/codelab-init-ssh.sh

# codelab
bash /init-lab/init_lab.sh CODELAB

echo "Codelab environment is ready."

exec bash -c "${OPENVSCODE_SERVER_ROOT}/bin/openvscode-server --port 8080 --host 0.0.0.0 --without-connection-token"
