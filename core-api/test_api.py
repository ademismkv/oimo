import requests
import argparse
import os
from pathlib import Path

def test_detect_ornaments(image_path, language="en", url="http://localhost:8000"):
    """Test the detect ornaments endpoint with a local image"""
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        return
    
    endpoint = f"{url}/detect/"
    
    # Prepare multipart form data
    files = {"file": (os.path.basename(image_path), open(image_path, "rb"), "image/jpeg")}
    data = {"language": language}
    
    print(f"Sending image {image_path} for ornament detection...")
    try:
        response = requests.post(endpoint, files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n--- Detection Results ---")
            if "detections" in result and result["detections"]:
                print(f"Found {len(result['detections'])} ornaments:")
                for i, detection in enumerate(result["detections"]):
                    print(f"\n{i+1}. Ornament: {detection['class']}")
                    print(f"   Confidence: {detection['confidence']:.4f}")
                    print(f"   Meaning: {detection.get('meaning', 'No meaning available')}")
                    print(f"   Bounding Box: {detection['bbox']}")
            else:
                print("No ornaments detected in the image.")
                
            if "new_ornament_folders" in result:
                print(f"\nCreated new folders for ornaments: {', '.join(result['new_ornament_folders'])}")
        else:
            print(f"Error: HTTP {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"Error making API request: {str(e)}")

def test_get_meaning(ornament_name, language="en", url="http://localhost:8000"):
    """Test the get meaning endpoint"""
    endpoint = f"{url}/meanings/{ornament_name}"
    params = {"language": language}
    
    print(f"Fetching meaning for ornament '{ornament_name}' in {language}...")
    try:
        response = requests.get(endpoint, params=params)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nOrnament: {result['ornament']}")
            print(f"Language: {result['language']}")
            print(f"Meaning: {result['meaning']}")
        else:
            print(f"Error: HTTP {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"Error making API request: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the Ornament Detection API")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Detect command
    detect_parser = subparsers.add_parser("detect", help="Detect ornaments in an image")
    detect_parser.add_argument("image_path", help="Path to the image file")
    detect_parser.add_argument("--language", "-l", default="en", choices=["en", "kg", "ru"], 
                               help="Language for meanings (en, kg, ru)")
    detect_parser.add_argument("--url", default="http://localhost:8000", 
                               help="API base URL")
    
    # Get meaning command
    meaning_parser = subparsers.add_parser("meaning", help="Get meaning for a specific ornament")
    meaning_parser.add_argument("ornament_name", help="Name of the ornament")
    meaning_parser.add_argument("--language", "-l", default="en", choices=["en", "kg", "ru"], 
                                help="Language for meaning (en, kg, ru)")
    meaning_parser.add_argument("--url", default="http://localhost:8000", 
                                help="API base URL")
    
    args = parser.parse_args()
    
    if args.command == "detect":
        test_detect_ornaments(args.image_path, args.language, args.url)
    elif args.command == "meaning":
        test_get_meaning(args.ornament_name, args.language, args.url)
    else:
        parser.print_help() 