#!/bin/bash

echo "Ornament Detection API Example"
echo "============================="
echo ""

# Check if an image file was provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <path-to-image-file>"
    echo "Example: $0 ../training/Singular-Ornament-Dataset-3/test/images/unity9_aug_11_jpg.rf.d1ef3b5e963f5c3a1bbd27bfa80fd76a.jpg"
    exit 1
fi

IMAGE_PATH=$1
LANGUAGE=${2:-"en"}  # Default to English if not specified

echo "Step 1: Make sure the API server is running in another terminal using:"
echo "cd core-api && ./run_api.sh"
echo ""

echo "Step 2: Testing the API using Python script"
echo "-------------------------------------"
echo "Running: python test_api.py detect $IMAGE_PATH --language $LANGUAGE"
echo ""

python test_api.py detect "$IMAGE_PATH" --language "$LANGUAGE"

echo ""
echo "Step 3: Testing the API using curl"
echo "------------------------------"
echo "Running curl command:"
echo "curl -X POST \"http://localhost:8000/detect/\" -H \"Content-Type: multipart/form-data\" -F \"file=@$IMAGE_PATH\" -F \"language=$LANGUAGE\""
echo ""

curl -X POST "http://localhost:8000/detect/" -H "Content-Type: multipart/form-data" -F "file=@$IMAGE_PATH" -F "language=$LANGUAGE"

echo ""
echo ""
echo "Done! Check the Dataset directory for saved ornament images." 