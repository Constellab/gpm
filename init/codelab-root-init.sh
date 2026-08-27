#!/bin/bash
# Root-only codelab startup steps, run by align-user.sh after the UID/GID remap
# and before privileges are dropped to labuser (see entrypoint-codelab.sh).

# Marker so the entrypoint can tell that this script already ran as root
# instead of re-running it via sudo.
mkdir -p /run
touch /run/codelab-root-init-done

# Ensure ${LAB_FOLDER} directory structure exists with correct permissions
# This fixes permissions when ${LAB_FOLDER} is mounted as a volume (volumes are created as root)
mkdir -p "${LAB_FOLDER}/user"
# Only chown if needed (avoids slow recursive operation on large directories)
if [ "$(stat -c %U "${LAB_FOLDER}")" != "labuser" ]; then
    chown labuser:labuser "${LAB_FOLDER}"
fi
if [ "$(stat -c %U "${LAB_FOLDER}/user")" != "labuser" ]; then
    chown labuser:labuser "${LAB_FOLDER}/user"
fi

# Start the SSH server. No-op unless ENABLE_SSH_SERVER is enabled — the codelab
# image defaults it to true, since VS Code Remote over SSH is a codelab feature.
bash /init-lab/init-ssh.sh
