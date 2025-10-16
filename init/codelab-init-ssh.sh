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
# Using SSH's native PermitUserEnvironment feature for simpler configuration
USER_HOME="/home/labuser"
ENV_FILE="$USER_HOME/.ssh/environment"

echo "Configuring SSH environment variables..."

# Create .ssh directory if it doesn't exist
mkdir -p "$USER_HOME/.ssh"
chmod 700 "$USER_HOME/.ssh"

# Export non-user-specific environment variables to SSH environment file
# SSH loads this file automatically when PermitUserEnvironment is enabled
# Note: This script must run as root during container startup to capture Docker env vars
env | grep -vE '^(HOME|USER|LOGNAME|MAIL|SHELL|PWD|OLDPWD|SHLVL|_)=' > "$ENV_FILE"

# Set correct permissions and ownership
chmod 600 "$ENV_FILE"
chown -R labuser:labuser "$USER_HOME/.ssh"

echo "SSH environment configured at $ENV_FILE"
echo "Captured $(wc -l < "$ENV_FILE") environment variables"
