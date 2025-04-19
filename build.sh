#!/bin/bash

# Install dependencies
cd frontend/team_sync_front
npm install
npm install -g @vue/cli

# Build the Vue app
npm run build

# Move the built files to the static directory
cd ../..
mkdir -p static
cp -r frontend/team_sync_front/dist/* static/ 