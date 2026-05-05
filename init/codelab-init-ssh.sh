#!/bin/bash

# To debug ssh server run :
# Stop the current SSH service
# > service ssh stop
# Run in debug mode (will show logs in real-time)
# > /usr/sbin/sshd -D -d
# End debug

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

# Ensure .ssh exists for SSH key auth (separate from the shell-env setup below).
mkdir -p /home/labuser/.ssh
chmod 700 /home/labuser/.ssh

# Propagate container env vars (PATH, VIRTUAL_ENV, etc.) into ~/.bashrc_docker_env
# so SSH login shells and interactive shells see the same environment.
bash /init-lab/setup-shell-env.sh
