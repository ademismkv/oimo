#!/usr/bin/env python3

import os
import sys
import re
from pathlib import Path

def find_pt_files(root_dir):
    """Find all .pt files in the directory tree"""
    print(f"Searching for .pt files in {root_dir}...")
    pt_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.pt'):
                full_path = os.path.join(root, file)
                size_mb = os.path.getsize(full_path) / (1024 * 1024)
                pt_files.append((full_path, size_mb))
    return sorted(pt_files, key=lambda x: x[1], reverse=True)  # Sort by file size

def update_model_path(main_py_path, new_model_path):
    """Update the model path in main.py"""
    # Normalize the path relative to core-api directory
    current_dir = os.path.dirname(main_py_path)
    rel_path = os.path.relpath(new_model_path, current_dir)
    
    print(f"Updating model path in {main_py_path} to {rel_path}...")
    
    with open(main_py_path, 'r') as file:
        content = file.read()
    
    # Replace the model path
    updated_content = re.sub(
        r'model_path\s*=\s*"[^"]+"',
        f'model_path = "{rel_path}"',
        content
    )
    
    # Write back to file
    with open(main_py_path, 'w') as file:
        file.write(updated_content)
    
    print(f"Updated model path in {main_py_path}")

def main():
    # Get the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    
    # Find all .pt files in the project
    pt_files = find_pt_files(project_root)
    
    if not pt_files:
        print("No .pt files found!")
        return 1
    
    print(f"\nFound {len(pt_files)} .pt files:")
    for i, (file_path, size_mb) in enumerate(pt_files):
        print(f"{i+1}. {file_path} ({size_mb:.2f} MB)")
    
    # Let user choose which file to use
    while True:
        choice = input("\nEnter the number of the model file to use (or 'q' to quit): ")
        if choice.lower() == 'q':
            return 0
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(pt_files):
                selected_file = pt_files[index][0]
                break
            else:
                print("Invalid selection, please try again.")
        except ValueError:
            print("Please enter a number or 'q'.")
    
    # Update main.py with the new path
    main_py_path = os.path.join(script_dir, "main.py")
    update_model_path(main_py_path, selected_file)
    
    print("\nModel path updated. You should now be able to run the API.")
    print("To start the API server, run: ./run_api.sh")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 