#!/bin/bash

echo "Setting up Ornament Detection API"
echo "================================"

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "ERROR: Python is not installed or not in PATH"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "Using Python $PYTHON_VERSION"

# Create Dataset directory if it doesn't exist
echo "Creating Dataset directory..."
mkdir -p ../Dataset

# Install requirements
echo "Installing Python requirements..."
pip install -r requirements.txt

# Check if the model exists
MODEL_PATH="../training/runs/detect/yolov8_custom/weights/best.pt"
if [ ! -f "$MODEL_PATH" ]; then
    echo "WARNING: YOLOv8 model not found at $MODEL_PATH"
    echo "Please ensure the model file is present before running the API"
fi

# Make run scripts executable
chmod +x run_api.sh
chmod +x run_example.sh

echo ""
echo "Setup complete!"
echo ""
echo "To run the API server:"
echo "  ./run_api.sh"
echo ""
echo "To test with an example image:"
echo "  ./run_example.sh <path-to-image-file> [language]"
echo "  Example: ./run_example.sh ../training/Singular-Ornament-Dataset-3/test/images/unity9_aug_11_jpg.rf.d1ef3b5e963f5c3a1bbd27bfa80fd76a.jpg en"
echo "" 