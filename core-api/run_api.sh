#!/bin/bash

# Kill any existing uvicorn processes
echo "Checking for existing uvicorn processes..."
pkill -f "uvicorn main:app" || echo "No existing server processes found."

# Wait a moment for ports to be released
sleep 1

# Start the server
echo "Starting Ornament Detection API server..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload 