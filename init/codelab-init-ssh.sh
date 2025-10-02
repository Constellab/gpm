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

echo "Starting SSH server..."
service ssh start

# Create profile script to export container environment variables for SSH sessions
# This preserves app configuration from docker-compose while letting SSH set user-specific vars
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

# List of user-specific variables that SSH should control (not inherited from root)
USER_VARS=("HOME" "USER" "LOGNAME" "MAIL" "SHELL" "PWD" "OLDPWD" "SHLVL")

# Export all current environment variables except user-specific ones
env | while IFS='=' read -r key value; do
    # Skip empty keys or user-specific variables
    if [ -z "$key" ]; then
        continue
    fi

    # Check if this is a user-specific variable
    skip=false
    for uvar in "${USER_VARS[@]}"; do
        if [[ "$key" == "$uvar" ]]; then
            skip=true
            break
        fi
    done

    if [ "$skip" = true ]; then
        continue
    fi

    # Escape quotes in the value
    escaped_value=$(printf '%s\n' "$value" | sed 's/"/\\"/g')
    echo "export $key=\"$escaped_value\"" >> "$PROFILE_FILE"
done

# Make the profile script executable
chmod +x "$PROFILE_FILE"

echo "Created environment profile at $PROFILE_FILE"

# Ensure labuser's .bash_profile exists and sources .bashrc
# This ensures both login and non-login shells get the same environment
USER_HOME="/home/labuser"

# Create/update .bash_profile to source .bashrc (for login shells)
if [ ! -f "$USER_HOME/.bash_profile" ] || ! grep -q "source.*bashrc" "$USER_HOME/.bash_profile"; then
    echo "" >> "$USER_HOME/.bash_profile"
    echo "# Source .bashrc for consistent environment" >> "$USER_HOME/.bash_profile"
    echo "if [ -f ~/.bashrc ]; then" >> "$USER_HOME/.bash_profile"
    echo "    source ~/.bashrc" >> "$USER_HOME/.bash_profile"
    echo "fi" >> "$USER_HOME/.bash_profile"
    chown labuser:labuser "$USER_HOME/.bash_profile"
fi

# Ensure .profile also sources .bashrc (fallback for some shells)
if [ ! -f "$USER_HOME/.profile" ] || ! grep -q "source.*bashrc" "$USER_HOME/.profile"; then
    echo "" >> "$USER_HOME/.profile"
    echo "# Source .bashrc for consistent environment" >> "$USER_HOME/.profile"
    echo "if [ -f ~/.bashrc ]; then" >> "$USER_HOME/.profile"
    echo "    source ~/.bashrc" >> "$USER_HOME/.profile"
    echo "fi" >> "$USER_HOME/.profile"
    chown labuser:labuser "$USER_HOME/.profile"
fi

echo "SSH environment configured successfully for labuser"
