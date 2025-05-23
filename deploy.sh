#!/bin/bash

# Comprehensive deploy script for Ornament API

echo "🚀 Starting Ornament Detection API deployment preparation..."
echo "Current directory: $(pwd)"

# Determine root directory
ROOT_DIR=$(pwd)

# Clean up any previous deployment files
echo "🧹 Cleaning up previous deployment files..."
rm -rf deployment/app/best.pt deployment/app/meanings.csv 2>/dev/null

# Create necessary directories
echo "📁 Creating deployment directories..."
mkdir -p deployment/app/static/uploads deployment/app/dataset

# Find the model file
MODEL_FOUND=false
echo "🔍 Looking for model file (best.pt)..."

for model_path in "$ROOT_DIR/core-api/best.pt" "$ROOT_DIR/training/runs/detect/yolov8_custom/weights/best.pt"; do
  if [ -f "$model_path" ]; then
    echo "✅ Found model at: $model_path"
    cp "$model_path" deployment/app/
    MODEL_FOUND=true
    break
  fi
done

if [ "$MODEL_FOUND" = false ]; then
  echo "❌ ERROR: Could not find model file (best.pt)"
  echo "Please copy your trained model to deployment/app/best.pt manually"
  exit 1
fi

# Find the meanings file
MEANINGS_FOUND=false
echo "🔍 Looking for meanings database..."

for meanings_path in "$ROOT_DIR/core-api/meanings.csv" "$ROOT_DIR/Dataset/meanings.csv"; do
  if [ -f "$meanings_path" ]; then
    echo "✅ Found meanings at: $meanings_path"
    cp "$meanings_path" deployment/app/
    MEANINGS_FOUND=true
    break
  fi
done

if [ "$MEANINGS_FOUND" = false ]; then
  echo "❌ ERROR: Could not find meanings.csv"
  echo "Please copy meanings.csv to deployment/app/ manually"
  exit 1
fi

# Create placeholder files for empty directories
touch deployment/app/static/uploads/.gitkeep
touch deployment/app/dataset/.gitkeep

# Checking if files were copied correctly
if [ -f "deployment/app/best.pt" ] && [ -f "deployment/app/meanings.csv" ]; then
  echo "✅ All files copied successfully!"
  echo ""
  echo "🚀 Deployment package ready! To deploy to Railway:"
  echo "1. cd deployment"
  echo "2. railway login (if not already logged in)"
  echo "3. railway up"
  echo ""
  echo "Or connect to GitHub and deploy through Railway Dashboard."
  exit 0
else
  echo "❌ Some files are missing in the deployment package."
  echo "Please check the errors above and fix them."
  exit 1
fi 