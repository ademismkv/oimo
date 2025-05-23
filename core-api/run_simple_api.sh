#!/bin/bash

echo "Starting Simple Ornament API (no YOLOv8 required)..."
uvicorn simple_api:app --reload --host 0.0.0.0 --port 8000 