#!/bin/bash

# Install dependencies
cd frontend/team_sync_front
npm install

# Build the Vue app using local vue-cli-service
./node_modules/.bin/vue-cli-service build

# Move the built files to the static directory
cd ../..
mkdir -p static
cp -r frontend/team_sync_front/dist/* static/ 