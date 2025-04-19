#!/bin/bash

# Build the Vue app
cd frontend/team_sync_front
npm install
npm run build

# Create static directory if it doesn't exist
cd ../..
mkdir -p static

# Copy the built files to static directory
cp -r frontend/team_sync_front/dist/* static/

# Print the contents of the static directory
echo "Static directory contents:"
ls -la static/

# Install Python dependencies
pip install -r requirements.txt 