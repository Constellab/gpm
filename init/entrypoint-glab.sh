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

    exec sudo -u labuser -E -H "$0" "$@"
fi

# glab
# default port=3000, ip=0.0.0.0
bash /init-lab/init_lab.sh GLAB
echo "Glab environment is ready."

# Start gws server
exec bash -c "gws server run --settings-path /lab/.sys/app/settings.json"
