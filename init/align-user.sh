#!/bin/bash
# Shared helper for glab/codelab entrypoints.
#
# Usage from an entrypoint:
#   source /init-lab/align-user.sh
#   align_labuser_and_switch "/lab" [pre_switch_hook]
#
# Behavior:
#   - If running as root and $1 is a bind-mounted directory with a non-root
#     owner, remap labuser's UID/GID to match that owner (so files created
#     inside the container match the host user's permissions).
#   - If a pre_switch_hook is provided (second arg), run it as root after
#     the remap and before dropping privileges — use this for steps that
#     legitimately need root (e.g. starting sshd).
#   - Re-exec the calling script as labuser, preserving the Dockerfile PATH
#     (sudo resets PATH to secure_path even with -E).
#   - If already running as non-root (e.g. `user:` set in compose), return
#     without doing anything so the caller can continue.

align_labuser_and_switch() {
    local mount_path="$1"
    local pre_switch_hook="$2"

    if [ "$(id -u)" != "0" ]; then
        return 0
    fi

    if [ -d "$mount_path" ]; then
        local target_uid target_gid
        target_uid=$(stat -c '%u' "$mount_path")
        target_gid=$(stat -c '%g' "$mount_path")

        if [ "$target_uid" != "0" ] && [ "$target_uid" != "$(id -u labuser)" ]; then
            groupmod -g "$target_gid" labuser 2>/dev/null || groupadd -g "$target_gid" labuser_host
            usermod -u "$target_uid" -g "$target_gid" labuser
            chown -R "$target_uid:$target_gid" /home/labuser
        fi
    fi

    if [ -n "$pre_switch_hook" ]; then
        bash "$pre_switch_hook"
    fi

    # sudo resets PATH to its secure_path even with -E; re-inject it explicitly
    # so pip-installed binaries (gws) and conda tools remain reachable.
    # BASH_SOURCE[1] is the caller script; "$@" from the caller is forwarded via ENTRYPOINT_ARGS.
    exec sudo -u labuser -E -H env PATH="$PATH" "${ENTRYPOINT_SCRIPT}" "${ENTRYPOINT_ARGS[@]}"
}
