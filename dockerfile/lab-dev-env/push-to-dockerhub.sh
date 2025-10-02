#!/bin/bash

# Script to build and push lab-dev-env Docker image to DockerHub

set -e  # Exit on error

# Configuration
IMAGE_NAME="lab-dev-env"
DOCKERHUB_USERNAME="${DOCKERHUB_USERNAME:-your-dockerhub-username}"
TAG="${TAG:-latest}"
FULL_IMAGE_NAME="${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${TAG}"

echo "Building Docker image: ${FULL_IMAGE_NAME}"
docker build -t "${FULL_IMAGE_NAME}" .

echo "Logging in to DockerHub..."
docker login

echo "Pushing image to DockerHub: ${FULL_IMAGE_NAME}"
docker push "${FULL_IMAGE_NAME}"

echo "Successfully pushed ${FULL_IMAGE_NAME} to DockerHub!"
