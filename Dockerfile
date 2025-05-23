FROM python:3.9-slim-bullseye AS builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8000

# Copy requirements first to leverage Docker cache
COPY core-api/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache/pip/* && \
    rm -rf /root/.cache/torch/*

# Final stage
FROM python:3.9-slim-bullseye

# Copy system dependencies
COPY --from=builder /usr/lib/x86_64-linux-gnu/libgl* /usr/lib/x86_64-linux-gnu/
COPY --from=builder /usr/lib/x86_64-linux-gnu/libglib* /usr/lib/x86_64-linux-gnu/
COPY --from=builder /usr/lib/x86_64-linux-gnu/libsm* /usr/lib/x86_64-linux-gnu/
COPY --from=builder /usr/lib/x86_64-linux-gnu/libxrender* /usr/lib/x86_64-linux-gnu/
COPY --from=builder /usr/lib/x86_64-linux-gnu/libxext* /usr/lib/x86_64-linux-gnu/

# Copy Python packages
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

# Set working directory
WORKDIR /app

# Create necessary directories
RUN mkdir -p static/uploads models

# Copy only the necessary application files
COPY core-api/main.py .
COPY core-api/meanings.csv .

# Clean up any potential cache files
RUN find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true && \
    find . -type f -name "*.pyc" -delete && \
    find . -type f -name "*.pyo" -delete && \
    find . -type f -name "*.pyd" -delete && \
    find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true

# Expose the port
EXPOSE ${PORT}

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"] 