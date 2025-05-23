# Ornament Detection Project

This project provides ornament detection capabilities using a trained YOLOv8 model for identifying ornaments in images.

## Project Structure

- **core-api/**: FastAPI application for ornament detection
- **training/**: YOLOv8 model training and evaluation scripts
- **Dataset/**: Auto-generated storage of detected ornaments (created when the API is used)

## Setup and Usage

### Core API

The Core API provides a web service for ornament detection:

1. Navigate to the core-api directory
2. Run the setup script:
   ```bash
   cd core-api
   chmod +x setup.sh
   ./setup.sh
   ```
3. Start the API server:
   ```bash
   ./run_api.sh
   ```
4. Access the web interface at http://localhost:8000

### Model Training and Evaluation

The training directory contains:
- YOLOv8 model training scripts
- Evaluation scripts for testing model performance
- Trained model weights

To evaluate the model:
```bash
cd training
python evaluate_model.py
```

## API Features

- Detect ornaments in images
- Return the meaning of ornaments in English, Kyrgyz, or Russian
- Automatically organize detected ornaments into dataset folders
- Web interface for easy interaction
- REST API endpoints for integration with other systems 