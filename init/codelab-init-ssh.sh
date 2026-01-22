#!/bin/bash

# To debug ssh server run :
# Stop the current SSH service
# > service ssh stop
# Run in debug mode (will show logs in real-time)
# > /usr/sbin/sshd -D -d
# End debug

# Ensure /lab directory structure exists with correct permissions
# This fixes permissions when /lab is mounted as a volume (volumes are created as root)
mkdir -p /lab/user
# Only chown if needed (avoids slow recursive operation on large directories)
if [ "$(stat -c %U /lab)" != "labuser" ]; then
    chown labuser:labuser /lab
fi
if [ "$(stat -c %U /lab/user)" != "labuser" ]; then
    chown labuser:labuser /lab/user
fi

# Copy the ssh config in the correct location
# we use copy here because the /etc/ssh directory is mounted from the host
# and we want to ensure that the sshd_config file is always up to date
echo "Copying SSH configuration..."
cp /tmp/sshd_config /etc/ssh/sshd_config

# Generate host keys if they don't exist
if [ ! -f /etc/ssh/ssh_host_rsa_key ]; then
    echo "Generating SSH host keys..."
    ssh-keygen -A
fi

# Ensure correct permissions
chmod 600 /etc/ssh/ssh_host_*_key
chmod 644 /etc/ssh/ssh_host_*_key.pub

# Unlock labuser account (SSH uses public key auth, not passwords)
# Change ! to * in shadow file to unlock without password
sed -i 's/^labuser:!/labuser:*/' /etc/shadow

# Disable pam_limits to avoid core dump errors in containers
sed -i 's/^session.*pam_limits.so/# &/' /etc/pam.d/sudo 2>/dev/null || true
sed -i 's/^session.*pam_limits.so/# &/' /etc/pam.d/common-session 2>/dev/null || true

# Start rsyslog for SSH logging
echo "Starting rsyslog service..."
# Create log file first
touch /var/log/auth.log
chmod 640 /var/log/auth.log
/usr/sbin/rsyslogd

echo "Starting SSH server..."
service ssh start

# Verify SSH is logging
echo "SSH server started. Logs available at /var/log/auth.log"

# Export container environment variables for SSH sessions
# Using shell profile approach (.bash_profile and .bashrc) for reliability
USER_HOME="/home/labuser"
BASHRC_ENV="$USER_HOME/.bashrc_docker_env"

echo "Configuring SSH environment variables..."

# Create .ssh directory if it doesn't exist (needed for SSH keys)
mkdir -p "$USER_HOME/.ssh"
chmod 700 "$USER_HOME/.ssh"

# Create bash environment file with all container environment variables
echo "# Docker container environment variables" > "$BASHRC_ENV"
echo "# Auto-generated on $(date)" >> "$BASHRC_ENV"
echo "" >> "$BASHRC_ENV"

# Add PATH from current environment to preserve container's PATH configuration
CUSTOM_PATH="/home/labuser/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/opt/conda/bin"
echo "export PATH=\"$CUSTOM_PATH\"" >> "$BASHRC_ENV"

# Export all non-user-specific environment variables
env | grep -vE '^(HOME|USER|LOGNAME|MAIL|SHELL|PWD|OLDPWD|SHLVL|PATH|_|SUDO_GID|SUDO_UID|SUDO_USER|SUDO_COMMAND|HOSTNAME|TERM)=' | while IFS='=' read -r key value; do
    if [ -n "$key" ]; then
        # Escape quotes in value
        escaped_value=$(printf '%s\n' "$value" | sed 's/"/\\"/g')
        echo "export $key=\"$escaped_value\"" >> "$BASHRC_ENV"
    fi
done

# Source the environment file from .bash_profile (for login shells like SSH)
# This ensures environment is loaded for SSH sessions
if [ -f "$USER_HOME/.bash_profile" ]; then
    if ! grep -q ".bashrc_docker_env" "$USER_HOME/.bash_profile"; then
        echo "" >> "$USER_HOME/.bash_profile"
        echo "# Source Docker container environment variables" >> "$USER_HOME/.bash_profile"
        echo "if [ -f ~/.bashrc_docker_env ]; then" >> "$USER_HOME/.bash_profile"
        echo "    source ~/.bashrc_docker_env" >> "$USER_HOME/.bash_profile"
        echo "fi" >> "$USER_HOME/.bash_profile"
    fi
else
    # Create .bash_profile if it doesn't exist
    echo "# Source Docker container environment variables" > "$USER_HOME/.bash_profile"
    echo "if [ -f ~/.bashrc_docker_env ]; then" >> "$USER_HOME/.bash_profile"
    echo "    source ~/.bashrc_docker_env" >> "$USER_HOME/.bash_profile"
    echo "fi" >> "$USER_HOME/.bash_profile"
fi

# Also add to .bashrc for interactive non-login shells (like VS Code terminals)
if [ -f "$USER_HOME/.bashrc" ]; then
    if ! grep -q ".bashrc_docker_env" "$USER_HOME/.bashrc"; then
        echo "" >> "$USER_HOME/.bashrc"
        echo "# Source Docker container environment variables" >> "$USER_HOME/.bashrc"
        echo "if [ -f ~/.bashrc_docker_env ]; then" >> "$USER_HOME/.bashrc"
        echo "    source ~/.bashrc_docker_env" >> "$USER_HOME/.bashrc"
        echo "fi" >> "$USER_HOME/.bashrc"
    fi
else
    # Create .bashrc if it doesn't exist
    echo "# Source Docker container environment variables" > "$USER_HOME/.bashrc"
    echo "if [ -f ~/.bashrc_docker_env ]; then" >> "$USER_HOME/.bashrc"
    echo "    source ~/.bashrc_docker_env" >> "$USER_HOME/.bashrc"
    echo "fi" >> "$USER_HOME/.bashrc"
fi

# Set correct permissions and ownership
chmod 644 "$BASHRC_ENV"
chown labuser:labuser "$BASHRC_ENV"
[ -f "$USER_HOME/.bash_profile" ] && chown labuser:labuser "$USER_HOME/.bash_profile"
[ -f "$USER_HOME/.bashrc" ] && chown labuser:labuser "$USER_HOME/.bashrc"

# Count environment variables (excluding the header comments and PATH)
VAR_COUNT=$(grep -c "^export" "$BASHRC_ENV" || echo "0")

echo "SSH environment configured:"
echo "  - ~/.bashrc_docker_env sourced by .bash_profile (SSH login shells)"
echo "  - ~/.bashrc_docker_env sourced by .bashrc (interactive shells)"
echo "Exported $VAR_COUNT environment variables (including PATH)"
