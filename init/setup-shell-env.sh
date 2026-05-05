#!/bin/bash
# Write container env vars into ~/.bashrc_docker_env so new shells
# (SSH sessions, VS Code integrated terminals, `docker exec -it ... bash`)
# get the same PATH/VIRTUAL_ENV the Dockerfile defines. Without this, the
# venv prompt `(.venv)` does not appear and tools may resolve outside the venv.
#
# Shared by codelab-init-ssh.sh and entrypoint-local-dev-env.sh.

set -e

USER_HOME="/home/labuser"
BASHRC_ENV="$USER_HOME/.bashrc_docker_env"

echo "Configuring shell environment variables..."

echo "# Docker container environment variables" > "$BASHRC_ENV"
echo "# Auto-generated on $(date)" >> "$BASHRC_ENV"
echo "" >> "$BASHRC_ENV"

# Pin PATH so the venv bin comes first — `python`/`pip` resolve into
# /home/labuser/.venv, matching the Dockerfile and what VS Code sees.
CUSTOM_PATH="/home/labuser/.venv/bin:/home/labuser/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/opt/conda/bin"
echo "export PATH=\"$CUSTOM_PATH\"" >> "$BASHRC_ENV"

# Export every container env var except shell-managed ones (HOME, PWD, …)
# and PATH (handled above).
env | grep -vE '^(HOME|USER|LOGNAME|MAIL|SHELL|PWD|OLDPWD|SHLVL|PATH|_|SUDO_GID|SUDO_UID|SUDO_USER|SUDO_COMMAND|HOSTNAME|TERM)=' | while IFS='=' read -r key value; do
    if [ -n "$key" ]; then
        escaped_value=$(printf '%s\n' "$value" | sed 's/"/\\"/g')
        echo "export $key=\"$escaped_value\"" >> "$BASHRC_ENV"
    fi
done

# Source from .bash_profile (login shells, e.g. SSH) and .bashrc (interactive
# non-login, e.g. VS Code integrated terminals).
for rc in "$USER_HOME/.bash_profile" "$USER_HOME/.bashrc"; do
    if [ ! -f "$rc" ] || ! grep -q ".bashrc_docker_env" "$rc"; then
        {
            echo ""
            echo "# Source Docker container environment variables"
            echo "if [ -f ~/.bashrc_docker_env ]; then"
            echo "    source ~/.bashrc_docker_env"
            echo "fi"
        } >> "$rc"
    fi
done

chmod 644 "$BASHRC_ENV"
chown labuser:labuser "$BASHRC_ENV"
[ -f "$USER_HOME/.bash_profile" ] && chown labuser:labuser "$USER_HOME/.bash_profile"
[ -f "$USER_HOME/.bashrc" ] && chown labuser:labuser "$USER_HOME/.bashrc"

VAR_COUNT=$(grep -c "^export" "$BASHRC_ENV" || echo "0")
echo "Shell environment configured:"
echo "  - ~/.bashrc_docker_env sourced by .bash_profile (login shells)"
echo "  - ~/.bashrc_docker_env sourced by .bashrc (interactive shells)"
echo "Exported $VAR_COUNT environment variables (including PATH)"
