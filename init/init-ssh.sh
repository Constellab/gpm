#!/bin/bash
# Start the SSH server — only if it is explicitly enabled.
#
# Shipped by the glab image and shared by glab and codelab. Runs as root,
# before the entrypoint drops privileges to labuser (see align-user.sh).
#
# ENABLE_SSH_SERVER gates everything below. When it is not truthy this script
# returns immediately: no host key is generated, no sshd and no rsyslog process
# is started, no port is opened. Installing the openssh-server package alone
# starts nothing — the container has no init system, this script is the only
# thing that ever launches sshd.
#
# To debug ssh server run :
# Stop the current SSH service
# > service ssh stop
# Run in debug mode (will show logs in real-time)
# > /usr/sbin/sshd -D -d
# End debug

# Marker so the entrypoint can tell that this script already ran as root
# (through the align-user.sh hook) instead of re-running it via sudo.
mkdir -p /run
touch /run/init-ssh-done

case "${ENABLE_SSH_SERVER:-false}" in
    true|True|TRUE|1|yes|on)
        ;;
    *)
        echo "SSH server disabled (ENABLE_SSH_SERVER=${ENABLE_SSH_SERVER:-false}), sshd is not started."
        exit 0
        ;;
esac

# Copy the ssh config in the correct location
# we use copy here because the /etc/ssh directory is mounted from the host
# and we want to ensure that the sshd_config file is always up to date
echo "Copying SSH configuration..."
cp /opt/glab/sshd_config /etc/ssh/sshd_config

# Generate host keys if they don't exist. The image ships without host keys on
# purpose (they are deleted at build time), so each container gets its own.
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
chown labuser:labuser /home/labuser/.ssh

# Propagate container env vars (PATH, VIRTUAL_ENV, etc.) into ~/.bashrc_docker_env
# so SSH login shells and interactive shells see the same environment.
bash /init-lab/setup-shell-env.sh
