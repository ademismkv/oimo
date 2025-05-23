#!/bin/bash

echo "Troubleshooting Ornament Detection API"
echo "====================================="

# Check Python and dependencies
echo -e "\n[1] Checking Python installation..."
which python || { echo "ERROR: Python not found!"; exit 1; }
python --version

echo -e "\n[2] Checking required libraries..."
python -c "import ultralytics; print(f'✓ ultralytics {ultralytics.__version__} found')" || echo "✗ ultralytics not installed"
python -c "import fastapi; print(f'✓ fastapi {fastapi.__version__} found')" || echo "✗ fastapi not installed"
python -c "import pandas; print(f'✓ pandas {pandas.__version__} found')" || echo "✗ pandas not installed"
python -c "import cv2; print(f'✓ opencv-python {cv2.__version__} found')" || echo "✗ opencv-python not installed"

# Check model file
echo -e "\n[3] Checking for model file..."
MODEL_PATH="../training/runs/detect/yolov8_custom/weights/best.pt"
if [ -f "$MODEL_PATH" ]; then
    echo "✓ Model file found at: $MODEL_PATH"
    echo "  File size: $(du -h $MODEL_PATH | cut -f1)"
else
    echo "✗ Model file NOT found at: $MODEL_PATH"
    
    # Check if parent directories exist
    if [ -d "../training" ]; then
        echo "  ✓ Directory exists: ../training"
    else
        echo "  ✗ Directory missing: ../training"
    fi
    
    if [ -d "../training/runs" ]; then
        echo "  ✓ Directory exists: ../training/runs"
    else
        echo "  ✗ Directory missing: ../training/runs"
    fi
    
    if [ -d "../training/runs/detect" ]; then
        echo "  ✓ Directory exists: ../training/runs/detect"
    else
        echo "  ✗ Directory missing: ../training/runs/detect"
    fi
    
    if [ -d "../training/runs/detect/yolov8_custom" ]; then
        echo "  ✓ Directory exists: ../training/runs/detect/yolov8_custom"
    else
        echo "  ✗ Directory missing: ../training/runs/detect/yolov8_custom"
    fi
    
    if [ -d "../training/runs/detect/yolov8_custom/weights" ]; then
        echo "  ✓ Directory exists: ../training/runs/detect/yolov8_custom/weights"
        echo "  Content of weights directory:"
        ls -la ../training/runs/detect/yolov8_custom/weights/
    else
        echo "  ✗ Directory missing: ../training/runs/detect/yolov8_custom/weights"
    fi
    
    echo -e "\n  Looking for alternative model files:"
    find ../training -name "*.pt" | while read file; do
        echo "  Found model: $file ($(du -h $file | cut -f1))"
    done
fi

# Check for meanings.csv
echo -e "\n[4] Checking for meanings.csv..."
if [ -f "meanings.csv" ]; then
    echo "✓ meanings.csv found"
    echo "  Content preview:"
    head -n 3 meanings.csv
else
    echo "✗ meanings.csv NOT found"
fi

# Check dataset directory
echo -e "\n[5] Checking Dataset directory..."
if [ -d "../Dataset" ]; then
    echo "✓ Dataset directory exists"
    COUNT=$(find ../Dataset -type d | wc -l)
    echo "  Contains $(($COUNT-1)) subdirectories"
else
    echo "✗ Dataset directory does NOT exist"
    echo "  Creating Dataset directory..."
    mkdir -p ../Dataset
fi

# Check ports
echo -e "\n[6] Checking if port 8000 is in use..."
if command -v lsof >/dev/null 2>&1; then
    lsof -i:8000 || echo "✓ Port 8000 is available"
elif command -v netstat >/dev/null 2>&1; then
    netstat -tuln | grep 8000 || echo "✓ Port 8000 is available"
else
    echo "? Cannot check port status (lsof/netstat not available)"
fi

# Try to load the model directly
echo -e "\n[7] Testing model loading with Python..."
python -c "
from ultralytics import YOLO
import os
try:
    model_path = '../training/runs/detect/yolov8_custom/weights/best.pt'
    print(f'Attempting to load model from: {model_path}')
    print(f'File exists: {os.path.exists(model_path)}')
    if os.path.exists(model_path):
        print(f'File size: {os.path.getsize(model_path)} bytes')
        model = YOLO(model_path)
        print('✓ Model loaded successfully')
        print(f'Model type: {type(model)}')
        print(f'Model classes: {model.names}')
    else:
        print('✗ Model file not found')
except Exception as e:
    print(f'✗ Error loading model: {str(e)}')
"

echo -e "\n[8] Checking API web server..."
if curl -s --head http://localhost:8000 >/dev/null; then
    echo "✓ API server is running"
    echo "  Testing API status endpoint..."
    curl -s http://localhost:8000/status | python -m json.tool
else
    echo "✗ API server is NOT running"
fi

echo -e "\nTroubleshooting complete. Check above for any issues."
echo -e "If you're still having problems, ensure you've installed dependencies with:\n"
echo -e "    pip install -r requirements.txt\n"
echo -e "Then try running the API server with:\n"
echo -e "    ./run_api.sh\n" 