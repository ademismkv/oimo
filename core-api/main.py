from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import http_exception_handler
import shutil
import os
import uuid
from pathlib import Path
import sys
import pandas as pd
import cv2
import numpy as np
import tempfile
from enum import Enum
import traceback
from typing import List, Dict, Any, Optional
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to path to import YOLO
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Try to import YOLO with detailed error handling
try:
    from ultralytics import YOLO
    logger.info("Successfully imported ultralytics")
except ImportError as e:
    logger.error(f"Failed to import ultralytics: {str(e)}")
    logger.error("Make sure ultralytics is installed: pip install ultralytics")
    raise

# Define language options
class Language(str, Enum):
    ENGLISH = "en"
    KYRGYZ = "kg"
    RUSSIAN = "ru"

app = FastAPI(title="Ornament Detection API",
             description="API for detecting and identifying ornaments using YOLOv8")

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom exception handler for 500 errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "error": str(exc),
            "trace": traceback.format_exc().split("\n")
        }
    )

# Load the trained model
model_path = "best.pt"
model = None

# Check if model file exists
if not os.path.exists(model_path):
    logger.error(f"Model file not found at {model_path}")
    logger.error(f"Current working directory: {os.getcwd()}")
    logger.error(f"Content of training/runs/detect/yolov8_custom/weights/: {os.listdir('../training/runs/detect/yolov8_custom/weights/') if os.path.exists('../training/runs/detect/yolov8_custom/weights/') else 'Directory not found'}")
else:
    try:
        model = YOLO(model_path)
        logger.info(f"Model loaded successfully from {model_path}")
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        logger.error(traceback.format_exc())

# Load meanings database
meanings_path = "meanings.csv"
try:
    meanings_df = pd.read_csv(meanings_path)
    logger.info(f"Meanings database loaded with {len(meanings_df)} entries")
except Exception as e:
    logger.error(f"Failed to load meanings database: {str(e)}")
    meanings_df = pd.DataFrame(columns=["name", "kg", "ru", "en"])

# Create Dataset directory if it doesn't exist
dataset_dir = "../Dataset"
os.makedirs(dataset_dir, exist_ok=True)

# Create static directory for uploaded images
static_dir = "static"
uploads_dir = os.path.join(static_dir, "uploads")
os.makedirs(uploads_dir, exist_ok=True)

# Mount static files directory
app.mount("/static", StaticFiles(directory=static_dir), name="static")

def process_image(image_path: str) -> Dict[str, Any]:
    """Process an image with YOLOv8 model and return detections"""
    if model is None:
        error_msg = "Model not loaded"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
    
    try:
        # Run inference
        logger.info(f"Processing image: {image_path}")
        results = model(image_path)
        
        # Process results
        all_detections = []
        unique_classes = {}  # To keep track of best detection for each class
        
        for r in results:
            boxes = r.boxes
            for box in boxes:
                conf = box.conf.item()
                if conf > 0.25:  # Confidence threshold
                    cls = int(box.cls.item())
                    cls_name = model.names[cls]
                    bbox = box.xyxy.tolist()[0]  # Convert to list
                    
                    detection = {
                        "class": cls_name,
                        "confidence": conf,
                        "bbox": bbox
                    }
                    
                    all_detections.append(detection)
                    
                    # Keep only the best confidence detection for each class
                    if cls_name not in unique_classes or conf > unique_classes[cls_name]["confidence"]:
                        unique_classes[cls_name] = detection
        
        # Convert unique classes dict to list
        unique_detections = list(unique_classes.values())
        
        # Log all detections and the filtered unique ones
        logger.info(f"Found {len(all_detections)} total detections")
        logger.info(f"Found {len(unique_detections)} unique ornament types")
        
        return {
            "detections": unique_detections,
            "all_detections_count": len(all_detections)
        }
    except Exception as e:
        logger.error(f"Error in process_image: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

def get_ornament_meaning(ornament_name: str, lang: Language = Language.ENGLISH) -> Optional[str]:
    """Get the meaning of an ornament in the specified language"""
    # Make the search case-insensitive
    ornament_name = ornament_name.lower()
    
    # Convert all names in the DataFrame to lowercase for comparison
    meanings_df['name_lower'] = meanings_df['name'].str.lower()
    
    # Search using the lowercase name
    ornament_row = meanings_df[meanings_df["name_lower"] == ornament_name]
    
    if not ornament_row.empty:
        return ornament_row.iloc[0][lang]
    
    # If no match found, log the issue
    logger.warning(f"No meaning found for ornament '{ornament_name}'")
    logger.info(f"Available ornaments: {', '.join(meanings_df['name'].tolist())}")
    
    return None

def save_to_dataset(image_path: str, class_name: str) -> List[str]:
    """Save image to Dataset folder organized by detected ornament class"""
    created_folders = []
    
    # Create directory if it doesn't exist
    class_dir = os.path.join(dataset_dir, class_name)
    if not os.path.exists(class_dir):
        os.makedirs(class_dir)
        created_folders.append(class_name)
        
    # Copy the image to the class directory with a unique name
    dest_filename = f"{class_name}_{uuid.uuid4()}.jpg"
    dest_path = os.path.join(class_dir, dest_filename)
    
    # Copy the image
    shutil.copy(image_path, dest_path)
    
    return created_folders

@app.get("/status")
async def status():
    """Get API and model status"""
    return {
        "status": "running",
        "model_loaded": model is not None,
        "model_path": model_path,
        "model_path_exists": os.path.exists(model_path),
        "meanings_loaded": len(meanings_df) > 0,
        "working_directory": os.getcwd(),
        "python_path": sys.path,
    }

@app.get("/", response_class=HTMLResponse)
async def home():
    """API home page with a simple upload form"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ornament Detection API</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                line-height: 1.6;
            }
            h1 {
                color: #2c3e50;
                margin-bottom: 20px;
            }
            .form-group {
                margin-bottom: 15px;
            }
            label {
                display: block;
                margin-bottom: 5px;
            }
            select, input[type="file"] {
                padding: 8px;
                width: 100%;
                box-sizing: border-box;
            }
            button {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 15px;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover {
                background-color: #2980b9;
            }
            .results {
                margin-top: 20px;
                padding: 15px;
                border: 1px solid #ddd;
                border-radius: 4px;
                display: none;
            }
            .detection {
                margin-bottom: 10px;
                padding: 10px;
                background-color: #f9f9f9;
                border-radius: 4px;
            }
            .loader {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #3498db;
                border-radius: 50%;
                width: 30px;
                height: 30px;
                animation: spin 2s linear infinite;
                margin: 20px auto;
                display: none;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            #result-img {
                max-width: 100%;
                margin-top: 20px;
            }
            .error-message {
                color: red;
                padding: 10px;
                background-color: #ffebee;
                border-radius: 4px;
                margin: 10px 0;
                display: none;
            }
        </style>
    </head>
    <body>
        <h1>Ornament Detection</h1>
        <p>Upload an image to detect ornaments and get their meanings.</p>
        
        <div class="form-group">
            <label for="file">Select image:</label>
            <input type="file" id="file" accept="image/*">
        </div>
        
        <div class="form-group">
            <label for="language">Choose language for meanings:</label>
            <select id="language">
                <option value="en">English</option>
                <option value="kg">Kyrgyz</option>
                <option value="ru">Russian</option>
            </select>
        </div>
        
        <button onclick="detectOrnaments()">Detect Ornaments</button>
        <button onclick="checkStatus()">Check API Status</button>
        
        <div class="loader" id="loader"></div>
        <div class="error-message" id="error-message"></div>
        
        <div class="results" id="results">
            <h2>Detection Results</h2>
            <div id="detections-container"></div>
            <img id="result-img" src="" alt="Processed image">
        </div>
        
        <div class="results" id="status-container" style="display:none">
            <h2>API Status</h2>
            <pre id="status-info"></pre>
        </div>
        
        <script>
        async function checkStatus() {
            document.getElementById('loader').style.display = 'block';
            document.getElementById('status-container').style.display = 'none';
            document.getElementById('error-message').style.display = 'none';
            
            try {
                const response = await fetch('/status');
                if (!response.ok) {
                    throw new Error(`HTTP error ${response.status}`);
                }
                
                const result = await response.json();
                document.getElementById('status-info').textContent = JSON.stringify(result, null, 2);
                document.getElementById('status-container').style.display = 'block';
            } catch (error) {
                showError(`Error checking status: ${error.message}`);
            } finally {
                document.getElementById('loader').style.display = 'none';
            }
        }
        
        function showError(message) {
            const errorElement = document.getElementById('error-message');
            errorElement.textContent = message;
            errorElement.style.display = 'block';
        }
        
        async function detectOrnaments() {
            const fileInput = document.getElementById('file');
            const language = document.getElementById('language').value;
            
            if (!fileInput.files || fileInput.files.length === 0) {
                showError('Please select an image');
                return;
            }
            
            const file = fileInput.files[0];
            const formData = new FormData();
            formData.append('file', file);
            formData.append('language', language);
            
            // Show loading spinner
            document.getElementById('loader').style.display = 'block';
            document.getElementById('results').style.display = 'none';
            document.getElementById('error-message').style.display = 'none';
            document.getElementById('status-container').style.display = 'none';
            
            try {
                const response = await fetch('/detect/', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || `HTTP error ${response.status}`);
                }
                
                const result = await response.json();
                displayResults(result, file);
                
            } catch (error) {
                showError(`Error: ${error.message}`);
                console.error(error);
            } finally {
                // Hide loading spinner
                document.getElementById('loader').style.display = 'none';
            }
        }
        
        function displayResults(result, originalFile) {
            const resultsDiv = document.getElementById('results');
            const detectionsContainer = document.getElementById('detections-container');
            
            // Clear previous results
            detectionsContainer.innerHTML = '';
            
            // Add summary of detection counts
            const summaryDiv = document.createElement('div');
            summaryDiv.innerHTML = `
                <p><strong>Results:</strong> Found ${result.unique_detections} unique ornament type(s) out of ${result.total_detections} total detection(s).</p>
            `;
            detectionsContainer.appendChild(summaryDiv);
            
            if (result.detections && result.detections.length > 0) {
                result.detections.forEach((detection, index) => {
                    const detectionDiv = document.createElement('div');
                    detectionDiv.className = 'detection';
                    detectionDiv.innerHTML = `
                        <h3>Ornament: ${detection.class}</h3>
                        <p><strong>Confidence:</strong> ${(detection.confidence * 100).toFixed(2)}%</p>
                        <p><strong>Meaning:</strong> ${detection.meaning || 'No meaning available'}</p>
                    `;
                    detectionsContainer.appendChild(detectionDiv);
                });
                
                // Display created folders if any
                if (result.new_ornament_folders) {
                    const foldersDiv = document.createElement('div');
                    foldersDiv.innerHTML = `<p><strong>New folders created:</strong> ${result.new_ornament_folders.join(', ')}</p>`;
                    detectionsContainer.appendChild(foldersDiv);
                }
            } else {
                detectionsContainer.innerHTML = '<p>No ornaments detected</p>';
            }
            
            // Show results container
            resultsDiv.style.display = 'block';
            
            // Display the original image
            const resultImg = document.getElementById('result-img');
            resultImg.src = URL.createObjectURL(originalFile);
        }
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/detect/")
async def detect_ornaments(file: UploadFile = File(...), 
                          language: Language = Form(Language.ENGLISH)):
    """
    Detect ornaments in an uploaded image and return their meanings
    """
    # Validate file
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Create a temporary file with proper extension
    temp_file = None
    
    try:
        # Create a proper temporary file that works cross-platform
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            temp_file = tmp.name
            # Save uploaded file to the temporary file
            shutil.copyfileobj(file.file, tmp)
        
        logger.info(f"Saved uploaded image to temporary file: {temp_file}")
        
        # Check if the file exists and has content
        file_stat = os.stat(temp_file)
        logger.info(f"Temporary file size: {file_stat.st_size} bytes")
        
        if file_stat.st_size == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        
        # Process the image
        result = process_image(temp_file)
        
        # Add meanings to the result
        for detection in result["detections"]:
            ornament_name = detection["class"]
            logger.info(f"Looking up meaning for ornament: {ornament_name}")
            
            meaning = get_ornament_meaning(ornament_name, language)
            if meaning:
                detection["meaning"] = meaning
                logger.info(f"Found meaning for {ornament_name}: {meaning[:30]}...")
            else:
                detection["meaning"] = f"No meaning available for '{ornament_name}'"
                logger.warning(f"No meaning found for '{ornament_name}' in {language}")
        
        # Get all unique ornament classes detected
        ornament_classes = [d["class"] for d in result["detections"]]
        
        # Save to dataset and track new folders
        new_folders = []
        for ornament_class in ornament_classes:
            new_folders.extend(save_to_dataset(temp_file, ornament_class))
            
        if new_folders:
            result["new_ornament_folders"] = new_folders
            
        # Include total detection count for reference
        result["total_detections"] = result.pop("all_detections_count", 0)
        result["unique_detections"] = len(result["detections"])
        
        logger.info(f"Successfully processed image with {result['unique_detections']} unique ornament types")
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
    
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
                logger.info(f"Removed temporary file: {temp_file}")
            except Exception as e:
                logger.warning(f"Failed to remove temporary file {temp_file}: {str(e)}")

@app.get("/meanings/{ornament_name}")
async def get_meaning(ornament_name: str, language: Language = Language.ENGLISH):
    """Get the meaning of a specific ornament"""
    meaning = get_ornament_meaning(ornament_name, language)
    if meaning:
        return {"ornament": ornament_name, "meaning": meaning, "language": language}
    else:
        raise HTTPException(status_code=404, detail=f"Ornament '{ornament_name}' not found")

@app.get("/")
async def root():
    """API root endpoint"""
    return {"message": "Ornament Detection API is running"}

@app.get("/debug")
async def debug():
    """Debug endpoint to check model labels and available meanings"""
    model_info = {}
    meanings_info = {}
    
    # Get model labels if model is loaded
    if model is not None:
        try:
            model_info["loaded"] = True
            model_info["classes"] = model.names
        except Exception as e:
            model_info["loaded"] = False
            model_info["error"] = str(e)
    else:
        model_info["loaded"] = False
    
    # Get available meanings
    if len(meanings_df) > 0:
        meanings_info["count"] = len(meanings_df)
        meanings_info["names"] = meanings_df["name"].tolist()
        
        # Show a sample of meanings
        sample = {}
        for name in meanings_df["name"].tolist()[:3]:  # Show first 3
            sample[name] = {
                "en": get_ornament_meaning(name, "en"),
                "kg": get_ornament_meaning(name, "kg"),
                "ru": get_ornament_meaning(name, "ru"),
            }
        meanings_info["samples"] = sample
    else:
        meanings_info["count"] = 0
    
    return {
        "model": model_info,
        "meanings": meanings_info,
        "working_directory": os.getcwd()
    } 