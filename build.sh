#!/bin/bash

# Build the frontend
cd frontend/team_sync_front
npm install
npm run build

# Move the built files to the correct location
cd ../..
mkdir -p backend/static
cp -r frontend/team_sync_front/dist/* backend/static/ 