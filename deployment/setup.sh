#!/bin/bash

# Prepare deployment package for Railway

echo "Preparing files for Railway deployment..."

# Create necessary directories
mkdir -p app/static/uploads app/dataset

# Copy model and data files
if [ -f "../core-api/best.pt" ]; then
  echo "Copying model file..."
  cp ../core-api/best.pt app/
elif [ -f "$(pwd)/../core-api/best.pt" ]; then
  echo "Copying model file from alternate path..."
  cp $(pwd)/../core-api/best.pt app/
else
  echo "Error: Model file not found at ../core-api/best.pt"
  echo "Current directory: $(pwd)"
  echo "Trying alternative paths..."
  
  # Try looking in different locations
  for possible_path in "../core-api/best.pt" "./core-api/best.pt" "$(pwd)/core-api/best.pt" "/Users/ademisamakova/oimo-api/oimo-api/core-api/best.pt"; do
    if [ -f "$possible_path" ]; then
      echo "Found model at $possible_path"
      cp "$possible_path" app/
      echo "Model copied successfully!"
      break
    fi
    echo "Not found at $possible_path"
  done
  
  # Check if the copy was successful
  if [ ! -f "app/best.pt" ]; then
    echo "ERROR: Could not find the model file. Please copy it manually."
    exit 1
  fi
fi

# Similar approach for meanings.csv
if [ -f "../core-api/meanings.csv" ]; then
  echo "Copying meanings database..."
  cp ../core-api/meanings.csv app/
elif [ -f "$(pwd)/../core-api/meanings.csv" ]; then
  echo "Copying meanings database from alternate path..."
  cp $(pwd)/../core-api/meanings.csv app/
else
  echo "Looking for meanings.csv in alternative locations..."
  
  for possible_path in "../core-api/meanings.csv" "./core-api/meanings.csv" "$(pwd)/core-api/meanings.csv" "/Users/ademisamakova/oimo-api/oimo-api/core-api/meanings.csv"; do
    if [ -f "$possible_path" ]; then
      echo "Found meanings at $possible_path"
      cp "$possible_path" app/
      echo "Meanings file copied successfully!"
      break
    fi
    echo "Not found at $possible_path"
  done
  
  # Check if the copy was successful
  if [ ! -f "app/meanings.csv" ]; then
    echo "ERROR: Could not find the meanings.csv file. Please copy it manually."
    exit 1
  fi
fi

# Create placeholder files for empty directories
touch app/static/uploads/.gitkeep
touch app/dataset/.gitkeep

echo "Setup complete! Deploy using 'railway up' or connect to GitHub" 