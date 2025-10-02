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

# Create profile script to source environment variables during SSH login
# With this, the environment vairbale defined in the docker-compose file are available
# when logging in ssh. 
# It must provide the same the environment variables of the docker-compose file
# It also starts the ssh server

echo "Starting SSH server..."
service ssh start

PROFILE_FILE="/etc/profile.d/codelab-environment.sh"

# Delete the file if it already exists
if [ -f "$PROFILE_FILE" ]; then
  rm -f "$PROFILE_FILE"
  echo "Removed existing profile script at $PROFILE_FILE"
fi

# Create new profile script with environment variables
echo "#!/bin/bash" > "$PROFILE_FILE"
echo "# Generated environment variables for codelab container" >> "$PROFILE_FILE"
echo "# Auto-generated on $(date)" >> "$PROFILE_FILE"
echo "" >> "$PROFILE_FILE"

# Export all current environment variables
env | while IFS='=' read -r key value; do
    # Escape quotes in the value
    escaped_value=$(printf '%s\n' "$value" | sed 's/"/\\"/g')
    echo "export $key=\"$escaped_value\"" >> "$PROFILE_FILE"
done

# Make the profile script executable
chmod +x "$PROFILE_FILE"

echo "Created environment profile at $PROFILE_FILE"

# Create/update .bashrc for labuser to source the profile
# .bashrc modification - Ensures the profile script is sourced even in non-login interactive shells
USER_HOME="/home/labuser"
if [ ! -f "$USER_HOME/.bashrc" ] || ! grep -q "codelab-environment.sh" "$USER_HOME/.bashrc"; then
    echo "" >> "$USER_HOME/.bashrc"
    echo "# Source codelab environment variables" >> "$USER_HOME/.bashrc"
    echo "if [ -f /etc/profile.d/codelab-environment.sh ]; then" >> "$USER_HOME/.bashrc"
    echo "    source /etc/profile.d/codelab-environment.sh" >> "$USER_HOME/.bashrc"
    echo "fi" >> "$USER_HOME/.bashrc"
    # Ensure correct ownership
    chown labuser:labuser "$USER_HOME/.bashrc"
fi

echo "SSH environment configured successfully"
