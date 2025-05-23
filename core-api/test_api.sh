#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Testing Ornament Detection API...${NC}\n"

# Test 1: Check API Status
echo -e "${GREEN}Test 1: Checking API Status${NC}"
curl -s http://localhost:8000/status | json_pp
echo -e "\n"

# Test 2: Debug Endpoint
echo -e "${GREEN}Test 2: Debug Endpoint${NC}"
curl -s http://localhost:8000/debug | json_pp
echo -e "\n"

# Test 3: Get Meaning for a Specific Ornament
echo -e "${GREEN}Test 3: Get Meaning for 'unity' ornament${NC}"
curl -s "http://localhost:8000/meanings/unity?language=en" | json_pp
echo -e "\n"

# Test 4: Upload and Detect Ornaments
echo -e "${GREEN}Test 4: Upload and Detect Ornaments${NC}"
echo "Note: This test requires an image file. Please provide the path to your test image:"
read -p "Enter image path: " image_path

if [ -f "$image_path" ]; then
    curl -s -X POST http://localhost:8000/detect/ \
        -F "file=@$image_path" \
        -F "language=en" | json_pp
else
    echo "Error: File not found at $image_path"
fi

echo -e "\n${BLUE}API Testing Complete${NC}" 