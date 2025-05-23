from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from enum import Enum
import shutil
import os
import uuid
import pandas as pd
import tempfile
from typing import Dict, Any, Optional, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define language options
class Language(str, Enum):
    ENGLISH = "en"
    KYRGYZ = "kg"
    RUSSIAN = "ru"

app = FastAPI(title="Simple Ornament API",
             description="Simple API for testing without YOLOv8")

# Create Dataset directory if it doesn't exist
dataset_dir = "../Dataset"
os.makedirs(dataset_dir, exist_ok=True)

# Create static directory for uploaded images
static_dir = "static"
uploads_dir = os.path.join(static_dir, "uploads")
os.makedirs(uploads_dir, exist_ok=True)

# Mount static files directory
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Load meanings database
meanings_path = "meanings.csv"
try:
    meanings_df = pd.read_csv(meanings_path)
    logger.info(f"Meanings database loaded with {len(meanings_df)} entries")
except Exception as e:
    logger.error(f"Failed to load meanings database: {str(e)}")
    meanings_df = pd.DataFrame(columns=["name", "kg", "ru", "en"])
    # Add a dummy entry for "unity" if the file doesn't exist
    if len(meanings_df) == 0:
        meanings_df = pd.DataFrame([{
            "name": "unity",
            "kg": "Биримдик оймо",
            "ru": "Орнамент «Единство»",
            "en": "The Unity Ornament"
        }])

def get_ornament_meaning(ornament_name: str, lang: Language = Language.ENGLISH) -> Optional[str]:
    """Get the meaning of an ornament in the specified language"""
    ornament_row = meanings_df[meanings_df["name"] == ornament_name]
    
    if not ornament_row.empty:
        return ornament_row.iloc[0][lang]
    return None

def save_to_dataset(image_path: str, ornament_name: str) -> List[str]:
    """Save image to Dataset folder for a specific ornament"""
    created_folders = []
    
    class_dir = os.path.join(dataset_dir, ornament_name)
    if not os.path.exists(class_dir):
        os.makedirs(class_dir)
        created_folders.append(ornament_name)
        
    # Copy the image to the class directory with a unique name
    dest_filename = f"{ornament_name}_{uuid.uuid4()}.jpg"
    dest_path = os.path.join(class_dir, dest_filename)
    
    # Copy the image
    shutil.copy(image_path, dest_path)
        
    return created_folders

@app.get("/", response_class=HTMLResponse)
async def home():
    """API home page with a simple upload form"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Simple Ornament API</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            h1, h2 {
                color: #2c3e50;
            }
            .form-group {
                margin-bottom: 15px;
            }
            label {
                display: block;
                margin-bottom: 5px;
            }
            select, input[type="file"], input[type="text"] {
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
                margin-right: 10px;
            }
            .results {
                margin-top: 20px;
                padding: 15px;
                border: 1px solid #ddd;
                border-radius: 4px;
                display: none;
            }
            .error {
                color: red;
                margin-top: 20px;
                padding: 15px;
                border: 1px solid #ffaaaa;
                border-radius: 4px;
                background-color: #ffeeee;
                display: none;
            }
        </style>
    </head>
    <body>
        <h1>Simple Ornament API</h1>
        <p>This is a simplified version of the API for testing.</p>
        
        <div class="form-group">
            <label for="file">Select image:</label>
            <input type="file" id="file" accept="image/*">
        </div>
        
        <div class="form-group">
            <label for="ornament">Ornament name:</label>
            <input type="text" id="ornament" value="unity" placeholder="Enter ornament name">
        </div>
        
        <div class="form-group">
            <label for="language">Choose language for meanings:</label>
            <select id="language">
                <option value="en">English</option>
                <option value="kg">Kyrgyz</option>
                <option value="ru">Russian</option>
            </select>
        </div>
        
        <button onclick="processImage()">Process Image</button>
        <button onclick="getMeaning()">Get Meaning</button>
        
        <div id="error" class="error"></div>
        <div id="results" class="results"></div>
        
        <script>
        async function processImage() {
            const fileInput = document.getElementById('file');
            const ornament = document.getElementById('ornament').value.trim();
            const language = document.getElementById('language').value;
            
            if (!fileInput.files || fileInput.files.length === 0) {
                showError('Please select an image');
                return;
            }
            
            if (!ornament) {
                showError('Please enter an ornament name');
                return;
            }
            
            try {
                const formData = new FormData();
                formData.append('file', fileInput.files[0]);
                formData.append('ornament_name', ornament);
                formData.append('language', language);
                
                const response = await fetch('/process/', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'An error occurred');
                }
                
                const result = await response.json();
                showResults(`
                    <h2>Result:</h2>
                    <p><strong>Ornament:</strong> ${result.ornament}</p>
                    <p><strong>Meaning:</strong> ${result.meaning || 'No meaning available'}</p>
                    ${result.new_folders ? `<p><strong>Created folders:</strong> ${result.new_folders.join(', ')}</p>` : ''}
                    <p><strong>Image saved to dataset!</strong></p>
                `);
                
            } catch (error) {
                showError(`Error: ${error.message}`);
            }
        }
        
        async function getMeaning() {
            const ornament = document.getElementById('ornament').value.trim();
            const language = document.getElementById('language').value;
            
            if (!ornament) {
                showError('Please enter an ornament name');
                return;
            }
            
            try {
                const response = await fetch(`/meanings/${ornament}?language=${language}`);
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'An error occurred');
                }
                
                const result = await response.json();
                showResults(`
                    <h2>Meaning:</h2>
                    <p><strong>Ornament:</strong> ${result.ornament}</p>
                    <p><strong>Language:</strong> ${result.language}</p>
                    <p><strong>Meaning:</strong> ${result.meaning}</p>
                `);
                
            } catch (error) {
                showError(`Error: ${error.message}`);
            }
        }
        
        function showResults(html) {
            const results = document.getElementById('results');
            results.innerHTML = html;
            results.style.display = 'block';
            document.getElementById('error').style.display = 'none';
        }
        
        function showError(message) {
            const error = document.getElementById('error');
            error.textContent = message;
            error.style.display = 'block';
            document.getElementById('results').style.display = 'none';
        }
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/process/")
async def process_image(
    file: UploadFile = File(...),
    ornament_name: str = Form(...),
    language: Language = Form(Language.ENGLISH)
):
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
        
        logger.info(f"Saved uploaded image to: {temp_file}")
        
        # Get meaning for the ornament
        meaning = get_ornament_meaning(ornament_name, language)
        
        # Save to dataset
        new_folders = save_to_dataset(temp_file, ornament_name)
        
        # Prepare result
        result = {
            "ornament": ornament_name,
            "meaning": meaning,
        }
        
        if new_folders:
            result["new_folders"] = new_folders
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except Exception as e:
                logger.warning(f"Failed to remove temporary file: {str(e)}")

@app.get("/meanings/{ornament_name}")
async def get_meaning(ornament_name: str, language: Language = Language.ENGLISH):
    """Get the meaning of a specific ornament"""
    meaning = get_ornament_meaning(ornament_name, language)
    if meaning:
        return {"ornament": ornament_name, "meaning": meaning, "language": language}
    else:
        raise HTTPException(status_code=404, detail=f"Ornament '{ornament_name}' not found")

@app.get("/status")
async def status():
    """Get API status"""
    return {
        "status": "running",
        "meanings_loaded": len(meanings_df) > 0,
        "available_languages": ["en", "kg", "ru"],
        "dataset_dir": dataset_dir,
        "working_directory": os.getcwd()
    } 