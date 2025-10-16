#!/bin/bash

# To debug ssh server run :
# Stop the current SSH service
# > service ssh stop
# Run in debug mode (will show logs in real-time)
# > /usr/sbin/sshd -D -d
# End debug

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
# Using both SSH's PermitUserEnvironment and .bashrc for VS Code compatibility
USER_HOME="/home/labuser"
ENV_FILE="$USER_HOME/.ssh/environment"
BASHRC_ENV="$USER_HOME/.bashrc_docker_env"

echo "Configuring SSH environment variables..."

# Create .ssh directory if it doesn't exist
mkdir -p "$USER_HOME/.ssh"
chmod 700 "$USER_HOME/.ssh"

# Export non-user-specific environment variables
# Format 1: SSH environment file (KEY=VALUE format)
# Format 2: Bashrc sourcing file (export KEY="VALUE" format)
env | grep -vE '^(HOME|USER|LOGNAME|MAIL|SHELL|PWD|OLDPWD|SHLVL|_)=' > "$ENV_FILE"

# Create a bash-compatible version for VS Code Remote SSH
echo "# Docker container environment variables" > "$BASHRC_ENV"
echo "# Auto-generated on $(date)" >> "$BASHRC_ENV"
while IFS='=' read -r key value; do
    if [ -n "$key" ]; then
        # Escape quotes in value
        escaped_value=$(printf '%s\n' "$value" | sed 's/"/\\"/g')
        echo "export $key=\"$escaped_value\"" >> "$BASHRC_ENV"
    fi
done < "$ENV_FILE"

# Source the environment file from .bashrc if not already present
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
chmod 600 "$ENV_FILE"
chmod 644 "$BASHRC_ENV"
chown labuser:labuser "$USER_HOME/.ssh/environment"
chown labuser:labuser "$BASHRC_ENV"
chown labuser:labuser "$USER_HOME/.bashrc"

echo "SSH environment configured:"
echo "  - ~/.ssh/environment (for regular SSH)"
echo "  - ~/.bashrc_docker_env (for VS Code Remote)"
echo "Captured $(wc -l < "$ENV_FILE") environment variables"
