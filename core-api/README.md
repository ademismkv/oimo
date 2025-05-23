# Ornament Detection API

This FastAPI application provides ornament detection services using a YOLOv8 model trained to recognize ornaments.

## Features

- Detect ornaments in uploaded images using YOLOv8
- Return the meaning of each ornament in English, Kyrgyz, or Russian
- Automatically save new ornament images to a dataset folder
- Create separate directories for newly identified ornaments

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Make sure the YOLOv8 model file is present at the expected path: `../training/runs/detect/yolov8_custom/weights/best.pt`

## Running the API

Start the FastAPI server:

```bash
cd core-api
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

## API Endpoints

### Detect Ornaments

**POST /detect/**

Upload an image to detect ornaments and get their meanings.

**Query Parameters:**
- `language` (optional): Language for the meanings (en, kg, ru). Default: en (English)

**Example using curl:**

```bash
# For English meanings (default)
curl -X POST "http://localhost:8000/detect/" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/image.jpg" \
  -F "language=en"

# For Kyrgyz meanings
curl -X POST "http://localhost:8000/detect/" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/image.jpg" \
  -F "language=kg"

# For Russian meanings
curl -X POST "http://localhost:8000/detect/" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/image.jpg" \
  -F "language=ru"
```

### Get Meaning for Specific Ornament

**GET /meanings/{ornament_name}**

Get the meaning of a specific ornament.

**Query Parameters:**
- `language` (optional): Language for the meaning (en, kg, ru). Default: en (English)

**Example:**

```bash
# For English meaning (default)
curl -X GET "http://localhost:8000/meanings/unity?language=en"

# For Kyrgyz meaning
curl -X GET "http://localhost:8000/meanings/unity?language=kg"

# For Russian meaning
curl -X GET "http://localhost:8000/meanings/unity?language=ru"
```

## Dataset Organization

When you upload images with ornaments, the system:

1. Creates a `Dataset` directory at the project root (if it doesn't already exist)
2. For each detected ornament in the image, creates a folder with the ornament name (if it doesn't exist)
3. Saves the uploaded image to each relevant ornament folder with a unique filename

For example, if an image contains "unity" and "kochkor" ornaments, both the "unity" and "kochkor" folders will get a copy of the image. 