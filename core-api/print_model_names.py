#!/usr/bin/env python3

from ultralytics import YOLO
import os

def main():
    # Try both local and original path
    model_paths = [
        "best.pt",  # Local copy
        "../training/runs/detect/yolov8_custom/weights/best.pt"  # Original path
    ]
    
    model = None
    for path in model_paths:
        if os.path.exists(path):
            print(f"Found model at: {path}")
            try:
                model = YOLO(path)
                break
            except Exception as e:
                print(f"Error loading model from {path}: {e}")
    
    if model is None:
        print("Could not load model from any path")
        return
    
    print("\nModel class names:")
    for idx, name in model.names.items():
        print(f"  {idx}: '{name}'")
    
    print("\nAdd these entries to meanings.csv:")
    for idx, name in model.names.items():
        print(f"{name},\"Meaning in Kyrgyz for {name}\",\"Meaning in Russian for {name}\",\"Meaning in English for {name}\"")

if __name__ == "__main__":
    main() 