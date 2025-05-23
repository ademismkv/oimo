from ultralytics import YOLO
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def evaluate_model():
    # Path to the trained model
    model_path = "runs/detect/yolov8_custom/weights/best.pt"
    
    # Path to the test data
    test_data_path = "Singular-Ornament-Dataset-3/data.yaml"
    test_img_dir = "Singular-Ornament-Dataset-3/test/images"
    
    # Check if directories and files exist
    if not os.path.exists(model_path):
        print(f"Error: Model path not found: {model_path}")
        return
    
    if not os.path.exists(test_data_path):
        print(f"Error: Test data YAML not found: {test_data_path}")
        return
    
    if not os.path.exists(test_img_dir):
        print(f"Error: Test images directory not found: {test_img_dir}")
        return
    
    # Create output directory for visualizations
    output_dir = "evaluation_results"
    os.makedirs(output_dir, exist_ok=True)
    
    # Load the model
    print(f"Loading model from {model_path}...")
    model = YOLO(model_path)
    
    # Try to evaluate the model on the test data
    try:
        print("Evaluating model on test data...")
        results = model.val(data=test_data_path)
        
        print("\nModel Evaluation Results:")
        print(f"mAP50-95: {results.box.map}")
        print(f"mAP50: {results.box.map50}")
        print(f"mAP75: {results.box.map75}")
        print(f"Precision: {results.box.mp}")
        print(f"Recall: {results.box.mr}")
    except Exception as e:
        print(f"Error during validation: {str(e)}")
        print("Skipping validation and continuing with image predictions...")
    
    # Run predictions on test images and save visualizations
    test_images = list(Path(test_img_dir).glob("*.jpg"))
    if not test_images:
        print(f"No test images found in {test_img_dir}")
        return
    
    print(f"\nProcessing {len(test_images)} test images...")
    
    # Prepare data for summary statistics
    confidences = []
    
    # Process each test image
    for i, img_path in enumerate(test_images):
        img_name = os.path.basename(img_path)
        print(f"Processing image {i+1}/{len(test_images)}: {img_name}")
        
        try:
            # Run prediction
            results = model(img_path, conf=0.25)
            
            # Save the prediction visualization
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    confidences.append(box.conf.item())
            
            # Save the annotated image
            output_path = os.path.join(output_dir, f"pred_{img_name}")
            img_annotated = results[0].plot()
            cv2.imwrite(output_path, img_annotated)
        except Exception as e:
            print(f"  Error processing image {img_name}: {str(e)}")
    
    # Calculate and print summary statistics
    if confidences:
        print("\nSummary Statistics:")
        print(f"Total detections: {len(confidences)}")
        print(f"Average confidence: {np.mean(confidences):.4f}")
        print(f"Min confidence: {min(confidences):.4f}")
        print(f"Max confidence: {max(confidences):.4f}")
        
        try:
            # Plot confidence distribution
            plt.figure(figsize=(10, 6))
            plt.hist(confidences, bins=10, alpha=0.7)
            plt.title('Distribution of Detection Confidences')
            plt.xlabel('Confidence')
            plt.ylabel('Count')
            plt.grid(True, alpha=0.3)
            plt.savefig(os.path.join(output_dir, 'confidence_distribution.png'))
            print(f"\nResults saved to {output_dir} directory")
        except Exception as e:
            print(f"Error creating confidence distribution plot: {str(e)}")
    else:
        print("No detections found in test images")

if __name__ == "__main__":
    evaluate_model() 