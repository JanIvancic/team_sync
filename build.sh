#!/bin/bash

# Install frontend dependencies
cd frontend/team_sync_front
npm install

# Build frontend
npm run build

# Return to root directory
cd ../..

# Install Python dependencies
pip install -r requirements.txt 