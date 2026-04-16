#!/bin/bash
set -e

# If docker-compose passed `user:`, we already run as the target UID/GID and
# this block is a no-op. If not (older sub-composes, manual runs), align
# labuser with the owner of the bind-mounted /lab before starting.
if [ "$(id -u)" = "0" ] && [ -d /lab ]; then
    TARGET_UID=$(stat -c '%u' /lab)
    TARGET_GID=$(stat -c '%g' /lab)

    if [ "$TARGET_UID" != "0" ] && [ "$TARGET_UID" != "$(id -u labuser)" ]; then
        groupmod -g "$TARGET_GID" labuser 2>/dev/null || groupadd -g "$TARGET_GID" labuser_host
        usermod -u "$TARGET_UID" -g "$TARGET_GID" labuser
        chown -R "$TARGET_UID:$TARGET_GID" /home/labuser
    fi

    # SSH init must run as root before we drop privileges
    bash /init-lab/codelab-init-ssh.sh

    exec sudo -u labuser -E -H "$0" "$@"
fi

# Running as labuser from here on
# (sudo -E in case the entrypoint was started directly as labuser via `user:`
#  in the compose, in which case SSH init hasn't run yet)
if ! pgrep -x sshd >/dev/null 2>&1; then
    sudo -E bash /init-lab/codelab-init-ssh.sh
fi

# codelab
bash /init-lab/init_lab.sh CODELAB

echo "Codelab environment is ready."

exec bash -c "${OPENVSCODE_SERVER_ROOT}/bin/openvscode-server --port 8080 --host 0.0.0.0 --without-connection-token"
