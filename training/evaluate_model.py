from ultralytics import YOLO
import os
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import cv2

def evaluate_model():
    # Path to the trained model
    model_path = "runs/detect/yolov8_custom/weights/best.pt"
    
    # Path to the test images directly
    test_img_dir = "Singular-Ornament-Dataset-3/test/images"
    
    # Check if directories exist
    if not os.path.exists(model_path):
        print(f"Error: Model path not found: {model_path}")
        return
    
    if not os.path.exists(test_img_dir):
        print(f"Error: Test images directory not found: {test_img_dir}")
        return
        
    # Create output directory
    output_dir = "evaluation_results"
    os.makedirs(output_dir, exist_ok=True)
    
    # Load the model
    print(f"Loading model from {model_path}...")
    model = YOLO(model_path)
    
    # Get test images
    test_images = list(Path(test_img_dir).glob("*.jpg"))
    if not test_images:
        print(f"No test images found in {test_img_dir}")
        return
        
    print(f"Found {len(test_images)} test images")
    
    # Prepare data for results
    results_data = []
    confidences = []
    
    # Process each test image
    for i, img_path in enumerate(test_images):
        img_name = os.path.basename(img_path)
        print(f"Processing image {i+1}/{len(test_images)}: {img_name}")
        
        # Run prediction
        results = model(img_path, conf=0.25)
        
        # Save the annotated image
        output_path = os.path.join(output_dir, f"pred_{img_name}")
        img_annotated = results[0].plot()
        cv2.imwrite(output_path, img_annotated)
        
        # Collect detection results
        img_results = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                conf = box.conf.item()
                bbox = box.xyxy.tolist()[0]
                confidences.append(conf)
                img_results.append({
                    "confidence": conf,
                    "bbox": bbox
                })
                print(f"  Detected Unity ornament with confidence: {conf:.4f}")
                
        results_data.append({
            "image": img_name,
            "detections": img_results
        })
    
    # Calculate and print summary statistics
    if confidences:
        print("\nSummary Statistics:")
        print(f"Total detections: {len(confidences)}")
        print(f"Average confidence: {np.mean(confidences):.4f}")
        print(f"Min confidence: {min(confidences):.4f}")
        print(f"Max confidence: {max(confidences):.4f}")
        
        # Plot confidence distribution
        plt.figure(figsize=(10, 6))
        plt.hist(confidences, bins=10, alpha=0.7)
        plt.title('Distribution of Detection Confidences')
        plt.xlabel('Confidence')
        plt.ylabel('Count')
        plt.grid(True, alpha=0.3)
        plt.savefig(os.path.join(output_dir, 'confidence_distribution.png'))
        print(f"\nResults saved to {output_dir} directory")
    else:
        print("No detections found in test images")

if __name__ == "__main__":
    evaluate_model() 