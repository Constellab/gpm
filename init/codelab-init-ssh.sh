#!/bin/bash

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
echo "" >> "$PROFILE_FILE"

# Add all environment variables directly to the profile script
echo "export LAB_ID=\"${LAB_ID}\"" >> "$PROFILE_FILE"
echo "export LAB_NAME=\"${LAB_NAME}\"" >> "$PROFILE_FILE"
echo "export LAB_MODE=\"${LAB_MODE}\"" >> "$PROFILE_FILE"
echo "export LAB_ENVIRONMENT=\"${LAB_ENVIRONMENT}\"" >> "$PROFILE_FILE"
echo "export LAB_PROD_API_URL=\"${LAB_PROD_API_URL}\"" >> "$PROFILE_FILE"
echo "export LAB_DEV_API_URL=\"${LAB_DEV_API_URL}\"" >> "$PROFILE_FILE"
echo "export SPACE_API_KEY=\"${SPACE_API_KEY}\"" >> "$PROFILE_FILE"
echo "export SPACE_API_URL=\"${SPACE_API_URL}\"" >> "$PROFILE_FILE"
echo "export SPACE_FRONT_URL=\"${SPACE_FRONT_URL}\"" >> "$PROFILE_FILE"
echo "export FRONT_URL=\"${FRONT_URL}\"" >> "$PROFILE_FILE"
echo "export FRONT_VERSION=\"${FRONT_VERSION}\"" >> "$PROFILE_FILE"
echo "export GPU=\"${GPU}\"" >> "$PROFILE_FILE"
echo "export VIRTUAL_HOST=\"${VIRTUAL_HOST}\"" >> "$PROFILE_FILE"
echo "export BIOTA_BIODATA_DIR=\"${BIOTA_BIODATA_DIR}\"" >> "$PROFILE_FILE"
echo "export OPENAI_API_KEY=\"${OPENAI_API_KEY}\"" >> "$PROFILE_FILE"
echo "export COMMUNITY_API_URL=\"${COMMUNITY_API_URL}\"" >> "$PROFILE_FILE"
echo "export COMMUNITY_FRONT_URL=\"${COMMUNITY_FRONT_URL}\"" >> "$PROFILE_FILE"
echo "export COMMUNITY_API_KEY=\"${COMMUNITY_API_KEY}\"" >> "$PROFILE_FILE"
echo "export GWS_CORE_DB_HOST=\"${GWS_CORE_DB_HOST}\"" >> "$PROFILE_FILE"
echo "export GWS_CORE_DB_USER=\"${GWS_CORE_DB_USER}\"" >> "$PROFILE_FILE"
echo "export GWS_CORE_DB_PASSWORD=\"${GWS_CORE_DB_PASSWORD}\"" >> "$PROFILE_FILE"
echo "export GWS_CORE_DB_NAME=\"${GWS_CORE_DB_NAME}\"" >> "$PROFILE_FILE"
echo "export GWS_CORE_DB_PORT=\"${GWS_CORE_DB_PORT}\"" >> "$PROFILE_FILE"
echo "export GWS_TEST_DB_HOST=\"${GWS_TEST_DB_HOST}\"" >> "$PROFILE_FILE"
echo "export GWS_TEST_DB_USER=\"${GWS_TEST_DB_USER}\"" >> "$PROFILE_FILE"
echo "export GWS_TEST_DB_PASSWORD=\"${GWS_TEST_DB_PASSWORD}\"" >> "$PROFILE_FILE"
echo "export GWS_TEST_DB_NAME=\"${GWS_TEST_DB_NAME}\"" >> "$PROFILE_FILE"
echo "export GWS_TEST_DB_PORT=\"${GWS_TEST_DB_PORT}\"" >> "$PROFILE_FILE"
echo "export GWS_BIOTA_DB_HOST=\"${GWS_BIOTA_DB_HOST}\"" >> "$PROFILE_FILE"
echo "export GWS_BIOTA_DB_USER=\"${GWS_BIOTA_DB_USER}\"" >> "$PROFILE_FILE"
echo "export GWS_BIOTA_DB_PASSWORD=\"${GWS_BIOTA_DB_PASSWORD}\"" >> "$PROFILE_FILE"
echo "export GWS_BIOTA_DB_NAME=\"${GWS_BIOTA_DB_NAME}\"" >> "$PROFILE_FILE"
echo "export GWS_BIOTA_DB_PORT=\"${GWS_BIOTA_DB_PORT}\"" >> "$PROFILE_FILE"
echo "export STREAMLIT_APP_SERVER_PORT=\"${STREAMLIT_APP_SERVER_PORT}\"" >> "$PROFILE_FILE"
echo "export STREAMLIT_APP_SERVER_HOST=\"${STREAMLIT_APP_SERVER_HOST}\"" >> "$PROFILE_FILE"

# Make the profile script executable
chmod +x "$PROFILE_FILE"

echo "Created environment profile at $PROFILE_FILE"
